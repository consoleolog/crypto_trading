import os
from typing import Union

import numpy as np
import pandas as pd
import pyupbit
from pandas import DataFrame
from pyupbit import Upbit
from sklearn.linear_model import LinearRegression

from config import get_logger
from model.crypto import Crypto


class CryptoUtil:
    def __init__(self, ticker: str, upbit:Upbit):
        self.upbit = upbit
        self.data_dir = f'{os.getcwd()}/data'
        self.ticker = ticker
        self.log = get_logger(ticker)

    def get_amount(self, ticker:str)-> Union[int, float]:
        try:
            balances = self.upbit.get_balances()
            for b in balances:
                if b['currency'] == ticker:
                    if b['balance'] is not None:
                        return float(b['balance'])
                    else:
                        return 0
            return 0
        except Exception as err:
            self.log.error(err)

    def ema(self, interval:str, count:int, ema_options: dict[str, int]):
        try:
            data = pyupbit.get_ohlcv(
                ticker=f"KRW-{self.ticker}",
                interval=interval,
                count=count
            )

            data["ema_short"] = data["close"].ewm(span=ema_options["short"],
                                                  min_periods=ema_options["short"]).mean().dropna().astype(int)
            data["ema_middle"] = data["close"].ewm(span=ema_options["middle"],
                                                   min_periods=ema_options["middle"]).mean().dropna().astype(int)
            data["ema_long"] = data["close"].ewm(span=ema_options["long"],
                                                 min_periods=ema_options["long"]).mean().dropna().astype(int)

            data["macd_upper"] = data["ema_short"] - data["ema_middle"]  # (상)
            data["macd_middle"] = data["ema_short"] - data["ema_long"]  # (중)
            data["macd_lower"] = data["ema_middle"] - data["ema_long"]  # (하)

            data = data.reset_index()
            data.rename(columns={"index": "date"}, inplace=True)

            data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
            data.dropna(inplace=True)

            return data
        except Exception as err:
            self.log.error(err)

    def get_my_price(self) -> Union[int, float]:
        price = 0
        count = 0
        try:
            df = pd.read_csv(f"{self.data_dir}/{self.ticker}/buy_sell.csv", encoding="utf-8")
            for i, data in df.iloc[::-1].iterrows():
                if data["buy/sell"] == "SELL":
                    return price
                elif data["buy/sell"] == "BUY":
                    price += data["market_price"]
                    count += 1
                return price / count
        except Exception as err:
            self.log.error(err)
            return 0

    def get_current_profit(self):
        if self.get_my_price() is not None and self.get_my_price() != 0:
            return (pyupbit.get_current_price(
            f"KRW-{self.ticker}") - self.get_my_price()) / self.get_my_price() * 100
        else:
            return 0

    def save_data(self, crypto: Crypto, stage: int)->None:
        try:
            with open(f'{self.data_dir}/{self.ticker}/data.csv', 'a', encoding='utf-8') as handler:
                handler.write(f"\n{crypto.date}")
                handler.write(f",{crypto.close}")
                handler.write(f",{stage}")
                handler.write(f",{crypto.ema_short}")
                handler.write(f",{crypto.ema_middle}")
                handler.write(f",{crypto.ema_long}")
                handler.write(f",{crypto.macd_upper}")
                handler.write(f",{crypto.macd_middle}")
                handler.write(f",{crypto.macd_lower}")
        except Exception as err:
            self.log.error(err)

    def save_predict_data(self, crypto: Crypto, stage: int)->None:
        try:
            with open(f'{self.data_dir}/{self.ticker}/predict_data.csv', 'a', encoding='utf-8') as handler:
                handler.write(f"\n{crypto.date}")
                handler.write(f",{stage}")
                handler.write(f",{crypto.ema_short}")
                handler.write(f",{crypto.ema_middle}")
                handler.write(f",{crypto.ema_long}")
                handler.write(f",{crypto.macd_upper}")
                handler.write(f",{crypto.macd_middle}")
                handler.write(f",{crypto.macd_lower}")
        except Exception as err:
            self.log.error(err)

    def create_model(self):
        data = self.ema("minute1", 120, {
                        "short": 10,
                        "middle": 20,
                        "long": 40
        })

        ema_short, ema_middle, ema_long = np.array(data["ema_short"]), np.array(data["ema_middle"]), np.array(data["ema_long"])

        macd_upper, macd_middle, macd_lower = np.array(data["macd_upper"]), np.array(data["macd_middle"]), np.array(
            data["macd_lower"])

        ema_short_model = LinearRegression().fit(ema_middle.reshape((-1, 1)), ema_short)
        ema_short_score = ema_short_model.score(ema_middle.reshape((-1, 1)), ema_short)

        ema_middle_model = LinearRegression().fit(ema_short.reshape((-1, 1)), ema_middle)
        ema_middle_score = ema_middle_model.score(ema_short.reshape((-1, 1)), ema_middle)

        ema_long_model = LinearRegression().fit(ema_middle.reshape((-1, 1)), ema_long)
        ema_long_score = ema_long_model.score(ema_middle.reshape((-1, 1)), ema_long)

        macd_upper_model = LinearRegression().fit(macd_middle.reshape((-1, 1)), macd_upper)
        macd_upper_score = macd_upper_model.score(macd_middle.reshape((-1, 1)), macd_upper)

        macd_middle_model = LinearRegression().fit(macd_upper.reshape((-1, 1)), macd_middle)
        macd_middle_score = macd_middle_model.score(macd_upper.reshape((-1, 1)), macd_middle)

        macd_lower_model = LinearRegression().fit(macd_middle.reshape((-1, 1)), macd_lower)
        macd_lower_socre = macd_lower_model.score(macd_middle.reshape((-1, 1)), macd_lower)

        return {
            "scores": {
                "ema_short": ema_short_score,
                "ema_middle": ema_middle_score,
                "ema_long": ema_long_score,
                "macd_upper": macd_upper_score,
                "macd_middle": macd_middle_score,
                "macd_lower": macd_lower_socre
            },
            "models": {
                "ema_short": ema_short_model,
                "ema_middle": ema_middle_model,
                "ema_long": ema_long_model,
                "macd_upper": macd_upper_model,
                "macd_middle": macd_middle_model,
                "macd_lower": macd_lower_model
            }
        }

