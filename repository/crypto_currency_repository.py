import os
from datetime import datetime

import pandas as pd
import pyupbit

from config import Provider


class CryptoCurrencyRepository:
    def __init__(self, provider: Provider):
        self.__upbit = provider.upbit
        self.__ticker = provider.ticker
        self.__data_path = f"{os.getcwd()}/data/{provider.ticker}"
        self.__log = provider.log

    def get_coin(self, interval = "minutes1", count = 120):
        try:
            data = pyupbit.get_ohlcv(f"KRW-{self.__ticker}", interval, count)
            data = data.reset_index()
            data.rename(columns={"index": "date"}, inplace=True)
            data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
            data.dropna(inplace=True)
            return data
        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)} ")

    def get_amount(self, ticker):
        try:
            balances = self.__upbit.get_balances()
            for b in balances:
                if b['currency'] == ticker:
                    if b['balance'] is not None:
                        return float(b['balance'])
                    else:
                        return 0
            return 0
        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)} ")

    def save_trading_history(self, code, data):
        datefmt = '%Y-%m-%d %H:%M:%S'
        try:
            create_time = datetime.fromisoformat(data["created_at"])
            df = {
                "date": [create_time.strftime(datefmt)],
                "ticker": [self.__ticker],
                "buy/sell": [code],
                "price": [data["price"]],
                "market_price": [data["market_price"]],
            }
            pd.DataFrame(df).to_csv(f"{self.__data_path}/trading_history.csv",
                                    mode="a", index=False, header=False, encoding="utf-8")
        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)} ")


    def save_coin_data(self, data, stage):
        try:
            last_data = data.iloc[-1]
            df = {
                "date": [last_data["date"]],
                "close": [last_data["close"]],
                "stage": [stage],
                "ema_short": [last_data["ema_short"]],
                "ema_middle": [last_data["ema_middle"]],
                "ema_long": [last_data["ema_long"]],
                "macd_upper": [last_data["macd_upper"]],
                "macd_middle": [last_data["macd_middle"]],
                "macd_lower": [last_data["macd_lower"]],
                "upper_result": [last_data["upper_result"]],
                "middle_result": [last_data["middle_result"]],
                "lower_result": [last_data["lower_result"]],
            }
            pd.DataFrame(df).to_csv(
                f"{self.__data_path}/data.csv",
                mode="a", index=False, header=False, encoding="utf-8")
        except Exception as err:
            self.__log.error(f"{self.__ticker} ERROR : {str(err)} ")