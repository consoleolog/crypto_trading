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

    def get_coin(self, interval):
        data = pyupbit.get_ohlcv(f"KRW-{self.__ticker}", interval)
        data = data.reset_index()
        data.rename(columns={"index":"date"}, inplace=True)
        data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
        data.dropna(inplace=True)
        return data

    def save_trading_history(self, code,data):
        datefmt = '%Y-%m-%d %H:%M:%S'
        create_time = datetime.fromisoformat(data["create_time"])
        df = {
            "date": [create_time.strftime(datefmt)],
            "ticker": [self.__ticker],
            "buy/sell": [code],
            "price": [data["price"]],
            "market_price": [data["market_price"]],
        }
        pd.DataFrame(df).to_csv(f"{self.__data_path}/trading_history.csv",
                                mode="a",index=False, header=False, encoding="utf-8")


    def save_coin_data(self, data, stage):
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
            mode="a" ,index=False, header=False, encoding="utf-8")

    def get_coin_history(self):
        return pd.read_csv(f"{self.__data_path}/data.csv", encoding="utf-8").tail(10)

    def get_trading_history(self):
        return pd.read_csv(f"{self.__data_path}/trading_history.csv", encoding="utf-8")