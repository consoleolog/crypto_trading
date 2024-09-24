from config import *

def send_mail():
    import os
    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '[Upbit] Trading Result files'
    msg['From'] = SMTP_FROM
    msg['To'] = SMTP_TO
    for filename in os.listdir('./data'):
        with open(f'./data/{filename}', 'rb') as f:
            file = MIMEBase("application", "octet-stream")
            file.set_payload(f.read())
        encoders.encode_base64(file)
        file.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg.attach(file)
    s = smtplib.SMTP('smtp.naver.com', 587)
    s.starttls()
    s.login(NAVER_ID, NAVER_PASSWORD)
    s.sendmail(SMTP_FROM, SMTP_TO, msg.as_string())
    s.close()
