#!/usr/bin/env python
# coding: utf-8

# In[ ]:

def lg_fota_send_mail():
    import os

    print(os.getcwd())

    import ftplib
    import os
    from datetime import datetime, timedelta
    from dateutil.parser import parse
    import time

    model_lists = [["LM-V500N", 'LM-V510N'], ["LM-G900N", "LM-Q920N", "LM-F100N"]]
    model_list = [element for array in model_lists for element in array]

    print(os.listdir("./data/"))
    sorted(["data/" + f for f in os.listdir("data/") if not "." in f])[0]
    resent_dir = list(reversed(["data/" + f for f in os.listdir("data") if not "." in f and not "raw" in f]))[0]

    print(resent_dir)


    def isnotebook():
        try:
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell':
                from IPython.display import display, HTML
                return True  # Jupyter notebook or qtconsole
            elif shell == 'TerminalInteractiveShell':
                return False  # Terminal running IPython
            else:
                return False  # Other type (?)
        except NameError:
            return False  # Probably standard Python interpreter

    print("running on notebook : ", isnotebook())

    # In[ ]:

    def file_select(id=1):

        if id == 1:
            key = "lg_fota_last90day"
        elif id == 2:
            key = "lg_fota_recent"

        lastdir = list(reversed(["data/" + f for f in os.listdir("data") if not "." in f and not "raw" in f]))[
            0]  # 최근 폴더

        lastdate = sorted([lastdir + "/" + f for f in os.listdir(lastdir) if key in f])[
            0]  ##가장 먼저 연동한 Data, 오전 8시에 근접할 가능성 높으니까..
        print(lastdate)
        return lastdate

    lg_fota_recent_fname = file_select(2)  # 최근 현황 출력 용
    file_select(1)  # 그래프 출력용, 90일 트렌드

    # In[3]:

    import pandas as pd

    # 일자별 업그레이드 가입자 현황 (90일)
    lg_fota_final = pd.read_csv(file_select(1), encoding='euc-kr')

    # 최근날짜 현황
    lg_fota_recent = pd.read_csv(file_select(2), encoding='euc-kr')

    # 최근 결과 #하루전 Data와 통합
    lastday1st = lg_fota_final["Date"].max()
    lastday2nd = lg_fota_final.loc[lg_fota_final["Date"] != lastday1st, 'Date'].max()

    print(lastday1st, lastday2nd)

    # Datatiem 형식으로 변경
    lg_fota_final['Date'] = pd.to_datetime(lg_fota_final['Date'], format='%Y-%m-%d')

    # In[4]:

    import matplotlib.pyplot as plt
    from datetime import datetime
    import matplotlib.dates as mdates
    import matplotlib as mpl

    # pd.options.display.float_format = '{:20,.2f}'.format

    marker = [".", "o", "v", "^", "<", ">", "1", "2", "3", "4", "s", "p", "*", "h", "H", "+", "x", "D", "d"]

    for model in model_list:
        data = lg_fota_final.loc[(lg_fota_final["MODEL"] == model)]
        x_column = 'Date'
        aggfunc = 'sum'
        values = 'COUNT'
        index = "Lable"
        pte_name = data['pet_name'].unique()[0]

        pivot_tabile = pd.pivot_table(data=data, index=index, columns=x_column, aggfunc=aggfunc, values=values).T
        pivot_tabile['Total'] = pivot_tabile.sum(axis=1)

        fig = plt.figure(figsize=(20, 6))
        ax = fig.add_subplot(1, 1, 1)
        #     plt.title(pte_name + "(" + model + ")", fontsize=20)

        mk_index = 0
        for sw in pivot_tabile.columns:

            if (sw == 'Total'):
                plt.plot(pivot_tabile[sw], ls=":", color='gray', marker="", label=sw)
            else:
                plt.plot(pivot_tabile[sw], '-', marker=marker[mk_index], markersize=4, label=sw)

            #         plt.axvline(x=datetime(2019,12,17), color='r', linestyle='--', linewidth=2)   #세로줄
            mk_index = (mk_index + 1) % (len(marker) - 1)

        plt.legend(loc=7, fontsize=13.5, bbox_to_anchor=(1.16, 0.5))

        # Grop 설정
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=1)

        plt.xticks(rotation=45, fontsize=12.3)

        ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

        fig.patch.set_facecolor('xkcd:white')
        fig.savefig(model + ".png", bbox_inches='tight')  # Use fig. here

        # 표출력, 마지막 연동 시점 기준
        df = lg_fota_recent.loc[lg_fota_recent['Model'] == model]
        df = df[['Acceptance Date', 'Model', 'SW Ver', 'Count', 'MS(%)', 'Total Count', 'Delta Count', 'Delta MS(%)',
                 'OS Version']].reset_index()
        print("< {}({}) : {}기준>".format(pte_name, model, str(lastday1st)))
        # display(HTML(df.to_html()))
        print("SUM {} / {}%".format(df["Count"].sum(), df["MS(%)"].sum()))
        print("========================================\n")

        if isnotebook():
            plt.show()
            display(HTML(df.to_html()))

    # In[6]:

    from email.mime.image import MIMEImage
    import smtplib

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication

    from os.path import basename

    class MailSender(object):
        def __init__(self, username, password, server='smtp.gmail.com', port=587, use_tls=True):
            self.username = username
            self.password = password
            self.server = server
            self.port = port
            self.use_tls = use_tls

        def send(self, sender, recipients, subject, message_plain='', message_html='', images=None, files=None):
            '''

            :param sender: str
            :param recipients: [str]
            :param subject: str
            :param message_plain: str
            :param message_html: str
            :param images: [{id:str, path:str}]
            :return: None
            '''

            msg_related = MIMEMultipart('related')

            msg_related['Subject'] = subject
            msg_related['From'] = sender
            msg_related['To'] = ', '.join(recipients)
            msg_related.preamble = 'This is a multi-part message in MIME format.'

            msg_alternative = MIMEMultipart('alternative')
            msg_related.attach(msg_alternative)

            plain_part = MIMEText(message_plain, 'plain')
            html_part = MIMEText(message_html, 'html')

            msg_alternative.attach(plain_part)
            msg_alternative.attach(html_part)

            if images:
                for image in images:
                    with open(image['path'], 'rb') as f:
                        msg_image = MIMEImage(f.read())
                        msg_image.add_header('Content-ID', '<{0}>'.format(image['id']))
                        msg_related.attach(msg_image)

            # Sending the mail

            if files:
                for f in files or []:
                    with open(f, "rb") as fil:
                        part = MIMEApplication(fil.read(), Name=basename(f))
                    # After the file is closed
                    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                    msg_related.attach(part)

            server = smtplib.SMTP('{0}:{1}'.format(self.server, self.port))
            try:
                if self.use_tls:
                    server.starttls()

                server.login(self.username, self.password)
                server.sendmail(sender, recipients, msg_related.as_string())
            #             print(msg_related.as_string())

            finally:
                server.quit()

        # In[45]:

        import os

        # directory = "./SS_FOTA_FTP"
        # os.chdir(directory)

        print(os.getcwd())

    # ! /usr/bin/python
    # -*- coding: utf-8 -*-
    # from mailsender import MailSender

    from tabulate import tabulate
    from premailer import transform

    def highlight_max(s):
        '''
        highlight the maximum in a Series yellow.
        '''
        is_max = s == s.max()
        retval = ['background-color: #ECEBEB' if v else '' for v in is_max]
        return retval

    styles = [
        dict(selector="th", props=[("font-size", "100%"),
                                   ("text-align", "center")])
    ]

    from connection_info import get_connection_info

    # Your IMAP Settings

    smtp_host = get_connection_info("gmail_smtp_host")
    username = get_connection_info("gmail_user")
    password = get_connection_info("gmail_pw")

    sender = username

    images = list()
    files = list()

    html_more = """
    <tr>
        <td align="center">
        <p><H1>[model]</H1></p>
        </td>
    </tr>
    <tr>
        <td width="100%" valign="top" bgcolor="d0d0d0" style="padding:5px;">              
        <img width="100%" height="100%" src="cid:[imgname_id]" />
        </td>
    </tr>
    <tr>
        <td width="1000" align="center" valign="top" bgcolor="white" style="padding:5px;border:2px solid #444444">
        {table1}        
    </tr>
    <tr>
        <td width="1000" align="center" valign="top" bgcolor="white" style="padding:5px;border:2px solid #444444">
        <p><H3>[total_data]</H3></p>
    </tr>
    <tr><td align="center"><p><H3> </H3></p></td></tr>


    {more}

    """

    page = 0
    total_page = len(model_lists)
    for models in model_lists:
        page += 1
        print(page, models)
        with open('template.html', encoding='UTF-8') as template_html, open('template.txt') as template_plain:
            message_html = template_html.read()
            message_plain = template_plain.read()

            message_html = message_html.format(Date="Data Sync Time : {} {}".format(lastday1st, "0800"),
                                               Date_d1="Delta Sync Time : {} {}".format(lastday2nd, "0800"),
                                               more="{more}")

            for model in models:
                df = lg_fota_recent.loc[lg_fota_recent['Model'] == model]
                pte_name = df["pet_name"].unique()[0]
                #         df = df[['pet_name', 'Model','AP_CP','Count','MS(%)','Total Count', 'Delta Count', 'Delta Total Count', 'ua_ver', 'OS Version','Last Version','First Open Date','Firmware Size (MB)','release_type','ue_type']].reset_index().drop("index", axis=1)
                df_print = df[['Acceptance Date', 'SW Ver', 'Count', 'MS(%)', 'Delta Count', 'Delta MS(%)',
                               'OS Version']].reset_index().drop("index", axis=1)

                html_add = html_more.replace("[imgname_id]", "img_" + model)
                html_add = html_add.replace("[model]", pte_name + "(" + model + ")")

                total = df['Total Count'].unique()[0]
                total_delta = df['Delta Total Count'].unique()[0]
                sign = "+"
                if (total_delta < 0):
                    sign = ""
                html_add = html_add.replace("[total_data]",
                                            'Total Count : {:,} ( {}{:,} )'.format(total, sign, total_delta))

                images.append({'id': "img_" + model, 'path': model + ".png"})

                message_html = message_html.replace('{more}', html_add)

                s = df_print.style.format(
                    {'Count': "{:,}", 'Delta Count': '{:+,}', 'MS(%)': '{:.2f}', 'Delta MS(%)': '{:+.2f}'}) \
                    .set_properties(**{'text-align': 'right'})

                # .set_properties(**{'text-align': 'right', 'padding': "2px", 'border': '1px', 'border-style': 'solid'})
                # .set_properties(**{'text-align': 'right', 'padding' : "2px", 'border':'1px', 'border-style' :'solid', 'border-color':'#DFDEDE'})
                # .apply(highlight_max, subset=['Count', 'MS(%)', 'Delta Count'])\
                # .set_table_styles(styles)

                message_html = message_html.replace('{table1}', transform(
                    s.render()))  # teams 공유를 위해 transform로 inline style로 변경 필요

            message_html = message_html.replace('{more}', "")

            print("images : ", images)

            if (page == total_page):  # 마지막 메일에 파일 첨부
                files.append(lg_fota_recent_fname)
                print("files: ", files)

            mail_sender = MailSender(username, password, server=smtp_host)

            if __name__ == "__main__":
                # 테스트 메일 #Jupyter 노트 북 또는 개별 모듈 실행시
                print("테스트 메일")
                mail_sender.send(sender,
                                 ["jungil.kwon@sktelecom.com", "58fc60be.o365skt.onmicrosoft.com@apac.teams.ms"],
                                 'LG FOTA 연동 현황 ({}/{})'.format(page, total_page), message_html=message_html,
                                 message_plain=message_plain, images=images, files=files)

                if isnotebook():
                    display(HTML(message_html))

            else:
                # Teams 공유 메일 주소
                mail_sender.send(sender, ["jungil.kwon@sktelecom.com", "kwac@sktelecom.com",
                                          "9164c98a.o365skt.onmicrosoft.com@apac.teams.ms"],
                                 'LG FOTA 연동 현황 ({}/{})'.format(page, total_page), message_html=message_html,
                                 message_plain=message_plain, images=images,
                                 files=files)

            # display(HTML(message_html))
            print("complet!!")

    # In[8]:
    # print(message_html)


## Start
if __name__ == "__main__":
    lg_fota_send_mail()

