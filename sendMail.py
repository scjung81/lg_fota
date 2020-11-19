# ver 1.0
import smtplib
from email.mime.text import MIMEText

username = "sdqiskt@gmail.com"
password = 'chzqaozxqohquxfp'

def sendMail(to=["jungil.kwon@sktelecom.com", "d99419a7.o365skt.onmicrosoft.com@apac.teams.ms"], title="title", text="Text"):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
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
