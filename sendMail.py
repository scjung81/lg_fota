# ver 1.0
import smtplib
from email.mime.text import MIMEText

from connection_info import get_connection_info
username = get_connection_info("gmail_user")
password = get_connection_info("gmail_pw")
smtp_host = get_connection_info("gmail_smtp_host")

def sendMail(to=["jungil.kwon@sktelecom.com", "d99419a7.o365skt.onmicrosoft.com@apac.teams.ms"], title="title", text="Text"):
    smtp = smtplib.SMTP(smtp_host, 587)
    # TLS 보안 시작
    smtp.starttls()
    # 로그인 인증
    smtp.login(username, password)

    msg = MIMEText(text)
    msg['Subject'] = title
    msg['To'] = ', '.join(to)
    smtp.sendmail('sdqiskt@gmail.com', to, msg.as_string())

    smtp.quit()
    print("success mail sending")

## Start
if __name__ == "__main__":
    sendMail()
