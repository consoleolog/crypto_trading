import os
from typing import Optional

import pandas as pd
import pyupbit
from pandas import DataFrame

from config import Provider
from repository.crypto_currency_repository import CryptoCurrencyRepository
from service.mail_service import MailService
from util.crypto_currency_util import CryptoCurrencyUtil

class CryptoCurrencyService:
    def __init__(self,
                 provider: Provider,
                 crypto_currency_repository: CryptoCurrencyRepository,
                 mail_service: MailService):
        self.__upbit = provider.upbit
        self.__ticker = provider.ticker
        self.__log = provider.log
        self.__mail_service = mail_service
        self.__crypto_currency_repository = crypto_currency_repository
        self.__data_path = f"{os.getcwd()}/data/{provider.ticker}"

    def start_trading(self, ema_options, price , interval="minute1"):
        try:
            data: Optional[DataFrame] = CryptoCurrencyUtil.get_macd(
                CryptoCurrencyUtil.get_ema(self.__crypto_currency_repository.get_coin(interval), ema_options)
            )

            stage = CryptoCurrencyUtil.get_stage(data)

            self.__response_stage(stage=stage, data=data, price=price)

            history = pd.read_csv(f"{self.__data_path}/data.csv", encoding="utf-8")

            if len(history) > 5000:
                history = history.iloc[:0, :]
                history.to_csv(f"{self.__data_path}/data.csv", encoding="utf-8", index=False)

            self.__crypto_currency_repository.save_coin_data(data, stage)

        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)} ")

    def get_krw(self):
        return self.__crypto_currency_repository.get_amount("KRW")

    def __get_my_price(self):
        price = 0
        count = 0
        try:
            df = pd.read_csv(f"{self.__data_path}/trading_history.csv", encoding="utf-8")
            for i, data in df.iloc[::-1].iterrows():
                if data["buy/sell"] == "SELL":
                    return price
                elif data["buy/sell"] == "BUY":
                    price += data["market_price"]
                    count += 1
                return price / count
        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)}")
            return 0

    def __response_stage(self, stage, data, price):
        try:
            if (stage == 4 and self.__crypto_currency_repository.get_amount(self.__ticker) == 0 and self.get_krw() > price > 6000
                            and all([data["upper_result"].iloc[-1] == True,
                                   data["middle_result"].iloc[-1] == True,
                                   data["lower_result"].iloc[-1] == True,
                                   data["middle_result"].iloc[-2] == True,])):
                self.__log.info(f"{self.__ticker} 매수 신호")
                self.__buy(price)
            elif (stage == 1 and self.__crypto_currency_repository.get_amount(self.__ticker) != 0 and self.__get_profit() > 0.15 and
                  all([data["upper_result"] == False,
                       data["middle_result"] == False])):
                self.__log.info(f"{self.__ticker} 매도 신호")
                self.__sell()
        except Exception as err:
            self.__log.error(f" {self.__ticker} ERROR : {str(err)} ")

    def __get_profit(self):
        if self.__get_my_price() is not None and self.__get_my_price() != 0:
            return (pyupbit.get_current_price(f"KRW-{self.__ticker}") - self.__get_my_price()) / self.__get_my_price() * 100
        else:
            return 0

    def create_crypto_currency_data_files(self):
        if not os.path.exists(self.__data_path):
            os.mkdir(self.__data_path)

        if not os.path.exists(f"{self.__data_path}/data.csv"):
            df_data = pd.DataFrame(columns=[
                "date", "close", "stage", "ema_short", "ema_middle", "ema_long",
                "macd_upper", "macd_middle", "macd_lower", "upper_result",
                "middle_result", "lower_result"
            ])
            df_data.to_csv(f"{self.__data_path}/data.csv", index=False, encoding="utf-8")

        if not os.path.exists(f"{self.__data_path}/trading_history.csv"):
            df_buy_sell = pd.DataFrame(columns=["date", "ticker", "buy/sell", "my_price", "market_price"])
            df_buy_sell.to_csv(f"{self.__data_path}/trading_history.csv", index=False, encoding="utf-8")


    def __buy(self, price):
        try:
            msg = self.__upbit.buy_market_order(f"KRW-{self.__ticker}", price)
            if isinstance(msg, dict):
                msg["market_price"] = pyupbit.get_current_price(f"KRW-{self.__ticker}")
                self.__crypto_currency_repository.save_trading_history("buy", msg)
                self.__log.debug(f"sending {self.__ticker} mail :: buy result ....")
                self.__mail_service.send_mail({
                    "content": f"{self.__ticker} 매수 결과 보고",
                    "filename": "trading_history.csv"
                })
        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)} ")

    def __sell(self):
        try:
            msg = self.__upbit.sell_market_order(f"KRW-{self.__ticker}", self.__crypto_currency_repository.get_amount(self.__ticker))
            if isinstance(msg, dict):
                self.__log.debug(f"sending {self.__ticker} mail :: sell result ....")
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.__ticker}")
                msg['price'] = 0
                self.__crypto_currency_repository.save_trading_history("sell", msg)
                self.__mail_service.send_mail({
                    "content": f"{self.__ticker} 매도 결과 보고",
                    "filename": "trading_history.csv"
                })
        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)} ")