from email.mime.text import MIMEText

from config import *

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class MailService:
    def __init__(self):
        self.root_dir = os.getcwd()

    def send_mail(self, content):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[Upbit] Trading Result files'
        msg['From'] = SMTP_FROM
        msg['To'] = SMTP_TO
        part = MIMEText(f"<h4>{content}</h4>", 'html')
        msg.attach(part)
        for filename in os.listdir(f'{self.root_dir}/data'):
            if filename != "crypto_history.csv":
                with open(f'{self.root_dir}/data/{filename}', 'rb') as f:
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

    def send_log_file(self, content):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[Upbit] {TICKER} Trading Result files'
        msg['From'] = SMTP_FROM
        msg['To'] = SMTP_TO
        part = MIMEText(f"<h4>{content}</h4>", 'html')
        msg.attach(part)
        with open(f'{self.root_dir}/logs/crypto.log', 'rb') as f:
            file = MIMEBase("application", "octet-stream")
            file.set_payload(f.read())
            encoders.encode_base64(file)
            file.add_header("Content-Disposition", f"attachment; filename=crypto.log")
            msg.attach(file)
        s = smtplib.SMTP('smtp.naver.com', 587)
        s.starttls()
        s.login(NAVER_ID, NAVER_PASSWORD)
        s.sendmail(SMTP_FROM, SMTP_TO, msg.as_string())
        s.close()

    def send_file(self, inputs):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[Upbit] {TICKER} Trading Result files'
        msg['From'] = SMTP_FROM
        msg['To'] = SMTP_TO
        part = MIMEText(f"<h4>{inputs['content']}</h4>", 'html')
        msg.attach(part)
        with open(f"{self.root_dir}/data/{inputs['filename']}", 'rb') as f:
            file = MIMEBase("application", "octet-stream")
            file.set_payload(f.read())
            encoders.encode_base64(file)
            file.add_header("Content-Disposition", f"attachment; filename=crypto.log")
            msg.attach(file)
        s = smtplib.SMTP('smtp.naver.com', 587)
        s.starttls()
        s.login(NAVER_ID, NAVER_PASSWORD)
        s.sendmail(SMTP_FROM, SMTP_TO, msg.as_string())
        s.close()