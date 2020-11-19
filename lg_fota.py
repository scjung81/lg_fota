# [20201119] git에소 추가
# 167 PC에서 commit 추가
# 개인 PC에서 주석 추가

from lg_fota_get_data_from_mail import lg_fota_get_data
from lg_fota_send_mail import lg_fota_send_mail

from sendMail import *
sendMail(title="lg_fota started ", text="")

lg_fota_get_data()
lg_fota_send_mail()

from sendMail import *
sendMail(title="lg_fota end ", text="")
