import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import Provider


class MailService:
    def __init__(self, provider: Provider):
        self.__naver_id = provider.naver_id
        self.__naver_password = provider.naver_password
        self.__smtp_from = provider.smtp_from
        self.__smtp_to = provider.smtp_to
        self.__ticker = provider.ticker
        self.__data_path = f"{os.getcwd()}/data/{provider.ticker}"
        self.__log = provider.log


    def send_mail(self, inputs: dict[str, str]) -> None:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{self.__ticker}] {inputs['content']}"
            msg['From'] = self.__smtp_from
            msg['To'] = self.__smtp_to
            part = MIMEText(f"<h4>{inputs['content']}</h4>", 'html')
            msg.attach(part)
            with open(f"{self.__data_path}/{self.__ticker}/{inputs['filename']}", 'rb') as handler:
                file = MIMEBase("application", "octet-stream")
                file.set_payload(handler.read())
                encoders.encode_base64(file)
                file.add_header("Content-Disposition", f"attachment; filename={inputs['filename']}")
                msg.attach(file)
            s = smtplib.SMTP('smtp.naver.com', 587)
            s.starttls()
            s.login(self.__naver_id, self.__naver_password)
            s.sendmail(self.__smtp_from, self.__smtp_to, msg.as_string())
            s.close()
        except Exception as err:
            self.__log.error(err)