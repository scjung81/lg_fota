from lg_fota_get_data_from_mail import lg_fota_get_data
from lg_fota_send_mail import lg_fota_send_mail

from sendMail import *
sendMail(title="lg_fota started ", text="")

lg_fota_get_data()  # Mail 서버 접속하여 LG FOTA 메일 다운로드 및 통계 Data 생성
lg_fota_send_mail() # 그래프 생성하여 메일 전달

from sendMail import *
sendMail(title="lg_fota end ", text="")
