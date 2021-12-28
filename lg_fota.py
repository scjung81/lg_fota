from lg_fota_get_data_from_mail import lg_fota_get_data
from lg_fota_send_mail import lg_fota_send_mail

from sendMail import *
sendMail(title="lg_fota started ", text="")

lg_fota_get_data()  # Mail 서버 접속하여 LG FOTA 메일 다운로드 및 통계 Data 생성
# test시 주석처리 필요

recevier_list = ["sukchan.jung@sktelecom.com", 'ywhan@sktelecom.com', 'jaehyun.ryu@sktelecom.com',
                 'jbmoon@sktelecom.com', 'jtchoi20@sktelecom.com', 'chris.mclee@sktelecom.com',
                 'jiyoun_choi@sktelecom.com', 'byungjo.min@sktelecom.com',
                 'jongkeunjung@sktelecom.com',
                 "9164c98a.o365skt.onmicrosoft.com@apac.teams.ms"]
recevier_list_test = ["58fc60be.o365skt.onmicrosoft.com@apac.teams.ms", "sukchan.jung@sktelecom.com"]

isTest = False
if (isTest == False) :
    lg_fota_send_mail(recevier_list) # 그래프 생성하여 메일 전달
else :
    lg_fota_send_mail(recevier_list_test)


from sendMail import *
sendMail(title="lg_fota end ", text="")
