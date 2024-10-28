import os
from os.path import dirname, join
from dotenv import load_dotenv
from pyupbit import Upbit

from logger import get_logger


class Provider:
    env_path = join(dirname(__file__), '.env')
    load_dotenv(env_path)
    def __init__(self, ticker):
        self.__openai_api_key=os.getenv("OPENAI_API_KEY")
        self.__upbit_access_key = os.getenv('UPBIT_ACCESS_KEY')
        self.__upbit_secret_key = os.getenv('UPBIT_SECRET_KEY')

        self.__naver_id = os.getenv('NAVER_ID')
        self.__naver_password = os.getenv('NAVER_PASSWORD')

        self.__smtp_from = os.getenv('SMTP_FROM')
        self.__smtp_to = os.getenv('SMTP_TO')

        self.__upbit = Upbit(self.__upbit_access_key, self.__upbit_secret_key)

        self.__ticker = ticker

        self.__log = get_logger(ticker)

    @property
    def log(self):
        return self.__log

    @property
    def ticker(self):
        return self.__ticker

    @property
    def openai_api_key(self):
        return self.__openai_api_key

    @property
    def upbit(self):
        return self.__upbit

    @property
    def naver_id(self):
        return self.__naver_id
    @property
    def naver_password(self):
        return self.__naver_password
    @property
    def smtp_from(self):
        return self.__smtp_from
    @property
    def smtp_to(self):
        return self.__smtp_to

