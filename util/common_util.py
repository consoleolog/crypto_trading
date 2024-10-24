import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SMTP_FROM, SMTP_TO, NAVER_PASSWORD, NAVER_ID
from config import get_logger

class CommonUtil:
    def __init__(self, ticker:str):
        self.data_dir = f'{os.getcwd()}/data'
        self.ticker = ticker
        self.log = get_logger(ticker)

    def init(self) -> None:
        try:
            if not os.path.exists(f"{os.getcwd()}/data/{self.ticker}"):
                os.mkdir(f"{os.getcwd()}/data/{self.ticker}")

            if not os.path.exists(f"{self.data_dir}/{self.ticker}/buy_sell.csv"):
                with open(f"{self.data_dir}/{self.ticker}/buy_sell.csv", "w", encoding="utf-8") as handler:
                    handler.write("date")
                    handler.write(",ticker")
                    handler.write(",buy/sell")
                    handler.write(",my_price")
                    handler.write(",market_price")

            if not os.path.exists(f"{self.data_dir}/{self.ticker}/data.csv"):
                with open(f"{self.data_dir}/{self.ticker}/data.csv", "w", encoding="utf-8") as handler:
                    handler.write("date")
                    handler.write(",close")
                    handler.write(",stage")
                    handler.write(",ema_short")
                    handler.write(",ema_middle")
                    handler.write(",ema_long")
                    handler.write(",macd_upper")
                    handler.write(",macd_middle")
                    handler.write(",macd_lower")
                    handler.write(",upper_result")
                    handler.write(",middle_result")
                    handler.write(",lower_result")

            if not os.path.exists(f"{self.data_dir}/{self.ticker}/predict_data.csv"):
                with open(f"{self.data_dir}/{self.ticker}/predict_data.csv", "w", encoding="utf-8") as handler:
                    handler.write("date")
                    handler.write(",stage")
                    handler.write(",ema_short")
                    handler.write(",ema_middle")
                    handler.write(",ema_long")
                    handler.write(",macd_upper")
                    handler.write(",macd_middle")
                    handler.write(",macd_lower")
                    handler.write(",upper_result")
                    handler.write(",middle_result")
                    handler.write(",lower_result")
        except Exception as err:
            self.log.error(err)

    def send_mail(self, inputs:dict[str, str])->None:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{self.ticker}] {inputs['content']}"
            msg['From'] = SMTP_FROM
            msg['To'] = SMTP_TO
            part = MIMEText(f"<h4>{inputs['content']}</h4>", 'html')
            msg.attach(part)
            with open(f"{self.data_dir}/{self.ticker}/{inputs['filename']}", 'rb') as handler:
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
        except Exception as err:
            self.log.error(err)