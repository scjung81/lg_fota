#!/usr/bin/env python
# coding: utf-8

def lg_fota_get_data():

    import smtplib
    import imaplib
    import email
    from email.mime.text import MIMEText
    import pandas as pd
    import shutil


    from datetime import datetime, timedelta
    from dateutil.parser import parse
    import time


    def getCurrentDate(t = 3):
        dayOfWeek = ['월', '화', '수', '목', '금', '토', '일']
        dt = datetime.now()

        if t == 1 :
            return dt.strftime("%A %d. %B %Y %H:%M:%S")
        elif t == 2 :
            return dt.strftime("%Y%m%d") +"("+ dayOfWeek[dt.weekday()] +")"
        elif t == 3 :
            return dt.strftime("%Y%m%d")
        elif t == 4 :
            return dt.strftime("%m%d")
        elif t == 5 :
            return dt.strftime("%Y%m%d") +"_"+ dayOfWeek[dt.weekday()] +"_"+ dt.strftime("%H%M%S")

    def getshiftday(day1, dayshift):
        date = parse(day1) + timedelta(days=dayshift)
        return date.strftime("%Y%m%d")

    today = getCurrentDate()
    yesterday = getshiftday(today, -1)

    print(today, yesterday)



    from email.header import decode_header

    def convet_header(text):
        if not text.startswith('=?'):
            return text

        name = ""
        for part in decode_header(text):
            name += str(*part)
        return name

    import imaplib
    import email.header
    import os
    import sys

    if not os.path.exists(os.path.join(os.getcwd(), "data")):
        os.makedirs(os.path.join(os.getcwd(), "data"))

    from connection_info import get_connection_info

    # Your IMAP Settings

    host = get_connection_info("gmail_imap_host")
    user = get_connection_info("gmail_user")
    password = get_connection_info("gmail_pw")

    # Connect to the server
    print('Connecting to ' + host)
    mailBox = imaplib.IMAP4_SSL(host)

    # Login to our account
    mailBox.login(user, password)

    boxList = mailBox.list()
    # print(boxList)

    mailBox.select("LG_FOTA")
    searchQuery = '(SUBJECT "FOTA")'
    # searchQuery = '(HEADER From "jungil.kwon@sk.com")'

    result, data = mailBox.uid('search', None, searchQuery)
    ids = data[0]
    # list of uids
    id_list = ids.split()[-10:]  #최근 수신된 10개 메일만 확인


    i = len(id_list)
    for x in range(i):
        latest_email_uid = id_list[x]

        # fetch the email body (RFC822) for the given ID
        result, email_data = mailBox.uid('fetch', latest_email_uid, '(RFC822)')
        # I think I am fetching a bit too much here...

        raw_email = email_data[0][1]

        # converts byte literal to string removing b''
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)


        # downloading attachments
        for part in email_message.walk():
            # this part comes from the snipped I don't understand yet...
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = convet_header(part.get_filename())#파일 명을 encoding에 맞춰 변환해 줘야 함.

            if bool(fileName):
                filePath = os.path.join('./data/raw/', fileName)
                if not os.path.isfile(filePath) :
                    if not os.path.exists("./data/raw/"):
                        os.makedirs("./data/raw/")
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()

    #     subject = str(email_message).split("Subject: ", 1)[1].split(f"\nTo:", 1)[0]
        subject = convet_header(email_message['Subject'])
        print('Downloaded "{file}" from email titled "{subject}" with UID {uid}.'.format(file=fileName, subject=subject, uid=latest_email_uid.decode('utf-8')))
        print('DATE:', email_message['Date'])

    mailBox.close()
    mailBox.logout()





    # print(os.listdir("data/"))
    # sorted(["data/"+ f for f in os.listdir("data/") if not "." in f])[0]

    def get_raw_data():
        file_list = list([ "data/raw/"+f for f in os.listdir("data/raw/") if not ".ipy" in f and not "backup" in f])
        return file_list

    #90일 이전 데이터는 backup 으로 이동
    backup_dir = 'data/raw/backup/'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    file_list = get_raw_data()

    max_day = max(file_list).split('_')[1].split('.')[0]
    last90day = getshiftday(max_day,-90)
    print("max_day : {}, last90day : {}".format(max_day, last90day))
    for file in file_list:
        day = file.split('_')[1].split('.')[0]
        if parse(day) < parse(last90day):
            print("backup : ", file)
            shutil.move(file, backup_dir)

    file_list = get_raw_data()
    file_list



    # 행 전개를 열전개로 변환
    default_column = ['MODEL', 'COUNTRY', 'BUYER', 'VERSION']
    day_list = ['COUNT', 'D-1', 'D-2','D-3', 'D-4', 'D-5', 'D-6', 'D-7']

    df_all = pd.DataFrame()

    for file in file_list:
        dt = file.split('_')[1].split('.')[0]

        df = pd.read_excel(file)

        for day in day_list:
            column = default_column.copy()
            column.append(day)
            t = df[column]
            t.rename(columns = {day:"COUNT"}, inplace=True)

            dm = 0
            if day != 'COUNT':
                dm = int(day.split('-')[1])
            date = getshiftday(dt, -dm)  #dt 계산
            t["Date"]= date
            t['Date'] = pd.to_datetime(t['Date'],format='%Y-%m-%d')


            t["Total Count"] = t.loc[t['VERSION'].str.contains('합계'), "COUNT"].iloc[0]
            t = t.loc[~t['VERSION'].str.contains('합계')]
            t["MS(%)"] = t["COUNT"] / t["Total Count"] * 100

            df_all = pd.concat([df_all,  t])

    df_all



    ver = df_all['VERSION'].str.split('-')
    df_all["ap"]  = ver.str[1]
    df_all["ua_ver"]  = df_all['MODEL'].str.split('-').str[1] + df_all["ap"].str[1:]
    df_all["First Open Date"]  = ver.str[4] + " " + ver.str[5] + " " + ver.str[6].str.split('+').str[0]
    df_all["First Open Date"] = pd.to_datetime(df_all["First Open Date"]).astype(str)

    # datetime.strptime(parse("{}-{}-{}".format(ver.str[4], ver.str[5], ver.str[6].str.split('+').str[0])), '%b %d %Y')

    # parse("SEP-07-2019")

    # "{}-{}-{}".format(ver.str[4], ver.str[5], ver.str[6].str.split('+').str[0])

    #중복 데이터 삭제, 오전 8시, 오후 5시 연동 될 경우 처음 데이터만 남김.. 오후 5시는 가입자 더 많아 지므로..
    df_all = df_all.sort_values(by=['MODEL','ap', 'VERSION', "Date", "COUNT"], ascending = True)
    df_all = df_all.drop_duplicates(['MODEL','ap', 'VERSION', "Date"], keep='first')

    # count 값이없는 행 제거
    df_all = df_all.loc[df_all["COUNT"].notnull()]

    #90 일 이전 제거
    dayago_90 = df_all["Date"].max() - timedelta(days=90) #90일 전
    print(dayago_90)
    df_all = df_all.loc[df_all["Date"] >= dayago_90]




    df_all = df_all.sort_values(by=["MODEL", "ap"])





    # # PLM 정보 통합


    def getNew_plm_sw():
        #마지막 폴더 찾기
        filepath = os.path.abspath('..') + "\\plm_selenium\\crawling\\data"
        lastdate = max([filepath +"/"+ f for f in os.listdir(filepath)], key=os.path.getctime)
        print(lastdate)

        path = os.path.join(os.getcwd(), lastdate, "plm_swver_DataWarehouse.xls")
        print(path)
        df = pd.read_excel(path)
        print(df.shape)
        return df

    plm_sw = getNew_plm_sw()
    plm_sw.head()



    col = ['manufacturer', 'pet_name', 'model', 'ua_model', 'ua_ver', 'ue_type', 'acceptance_date', 'release_sw', 'ongoing', 'release_type', 'os_type', 'os_ver', 'codeName']
    plm_sw= plm_sw.loc[plm_sw['manufacturer']=='LG전자', col]
    plm_sw.tail()




    a1 = pd.merge(df_all, plm_sw, left_on=['MODEL', 'ua_ver'], right_on=['model', 'ua_ver'], how='inner' )  #PLM 에 없는 Data 는 제거



    lg_fota_final = pd.concat([a1]).sort_values(by=["MODEL", "ap"])
    lg_fota_final



    lg_fota_final['Lable'] = lg_fota_final['ap'] + "(" + lg_fota_final['acceptance_date'] + ")"
    lg_fota_final[['Lable', 'acceptance_date', 'First Open Date']]



    lastdate = lg_fota_final["Date"].max().strftime("%Y%m%d")
    if not os.path.exists('data/'+lastdate):
        os.makedirs('data/'+lastdate)

    fname  = 'data/'+lastdate+"/lg_fota_last90days_" + lastdate + ".csv"
    print(fname)

    lg_fota_final.to_csv(fname, encoding='euc-kr', index=False)



    #최근 결과 #하루전 Data와 통합
    lastday1st = lg_fota_final["Date"].max()
    lastday2nd = lg_fota_final.loc[lg_fota_final["Date"]!= lastday1st, 'Date'].max()

    print(lastday1st, lastday2nd)

    lg_fota_recent = lg_fota_final.loc[lg_fota_final["Date"]== lastday1st, ['acceptance_date', 'pet_name', "MODEL", "ap", "ua_ver", "COUNT", 'MS(%)',  "Total Count", 'os_ver', 'codeName', "os_type", 'Date']]
    lg_fota_recent2nd = lg_fota_final.loc[lg_fota_final["Date"]== lastday2nd, ["MODEL", "ua_ver", "COUNT", "Total Count", 'MS(%)','Date']]
    lg_fota_recent2nd.rename(columns = {'COUNT' : 'COUNT_D-1', 'Total Count' : 'Total Count_D-1', 'Date' : 'Date_D-1', 'MS(%)':'MS(%)_D-1'}, inplace = True)
    lg_fota_recent = pd.merge(lg_fota_recent, lg_fota_recent2nd, on=['MODEL', 'ua_ver'], how='outer')

    lg_fota_recent["Delta Count"] =  lg_fota_recent["COUNT"] - lg_fota_recent["COUNT_D-1"]
    lg_fota_recent["Delta Total Count"] = lg_fota_recent["Total Count"] - lg_fota_recent["Total Count_D-1"]
    lg_fota_recent["Delta MS(%)"] = lg_fota_recent["MS(%)"] - lg_fota_recent["MS(%)_D-1"]
    lg_fota_recent["Delta MS(%)"] = lg_fota_recent["Delta MS(%)"].round(2)
    lg_fota_recent["MS(%)"] = lg_fota_recent["MS(%)"].round(2)

    lg_fota_recent.rename(columns = {'COUNT' : 'Count', 'MODEL' : 'Model'}, inplace = True)

    coun_list = [p for p in lg_fota_recent.columns if "Count" in p]
    lg_fota_recent[coun_list] = lg_fota_recent[coun_list].fillna(0.0).astype(int) #int type 변환

    lg_fota_recent["os_ver"].astype('float')
    lg_fota_recent.loc[lg_fota_recent['codeName']=="Android 10", 'codeName'] = "Q"
    lg_fota_recent["OS Version"] = lg_fota_recent['codeName'] + "(" + lg_fota_recent['os_type'] + lg_fota_recent['os_ver'] + ")"

    lg_fota_recent.rename(columns = {'ap' : 'SW Ver', 'acceptance_date' : 'Acceptance Date'}, inplace = True)
    lg_fota_recent = lg_fota_recent.reset_index().drop("index", axis=1)

    lg_fota_recent_fname  = 'data/'+lastdate+"/lg_fota_recent_" + lastdate + ".csv"
    lg_fota_recent.to_csv(lg_fota_recent_fname, encoding='euc-kr', index=False)
    lg_fota_recent

    print("Complete getting lg fota data form email ")


## Start
if __name__ == "__main__":
    lg_fota_get_data()

