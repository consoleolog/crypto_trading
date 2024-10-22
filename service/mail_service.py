from email.mime.text import MIMEText

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from config import SMTP_FROM, SMTP_TO, NAVER_ID, NAVER_PASSWORD
from logger import get_logger


class MailService:
    def __init__(self, ticker:str):
        self.root_dir = os.getcwd()
        self.TICKER = ticker
        self.log = get_logger(ticker)

    def send_file(self, inputs:dict[str, str])->type(None):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[{self.TICKER}] {inputs['content']}"
        msg['From'] = SMTP_FROM
        msg['To'] = SMTP_TO
        part = MIMEText(f"<h4>{inputs['content']}</h4>", 'html')
        msg.attach(part)
        with open(f"{self.root_dir}/data/{self.TICKER}/{inputs['filename']}", 'rb') as handler:
            file = MIMEBase("application", "octet-stream")
            file.set_payload(handler.read())
            encoders.encode_base64(file)
            file.add_header("Content-Disposition", f"attachment; filename={inputs['filename']}")
            msg.attach(file)
        s = smtplib.SMTP('smtp.naver.com', 587)
        s.starttls()
        s.login(NAVER_ID, NAVER_PASSWORD)
        s.sendmail(SMTP_FROM, SMTP_TO, msg.as_string())
        s.close()