import os
from typing import Union

import pandas as pd
import pyupbit
from pandas import DataFrame
from pyupbit import Upbit

from logger import get_logger
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
            data["signal"] = data["close"].ewm(span=ema_options["signal"],
                                               min_periods=ema_options["signal"]).mean().dropna().astype(int)

            data["macd_upper"] = data["ema_short"] - data["ema_middle"]  # (상)
            data["macd_middle"] = data["ema_short"] - data["ema_long"]  # (중)
            data["macd_lower"] = data["ema_middle"] - data["ema_long"]  # (하)

            data['macd_upper_slope'] = data['macd_upper'].diff()
            data['macd_middle_slope'] = data['macd_middle'].diff()
            data['macd_lower_slope'] = data['macd_lower'].diff()

            data['close_slope'] = data['close'].diff()

            data['ema_short_slope'] = data['ema_short'].diff()
            data['ema_middle_slope'] = data['ema_middle'].diff()
            data['ema_long_slope'] = data['ema_long'].diff()

            data['signal_slope'] = data['signal'].diff()

            data['histogram_upper'] = data['macd_upper'] - data['signal']
            data['histogram_middle'] = data['macd_middle'] - data['signal']
            data['histogram_lower'] = data['macd_lower'] - data['signal']

            data = data.reset_index()
            data.rename(columns={"index": "date"}, inplace=True)

            data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
            data.dropna(inplace=True)

            return data
        except Exception as err:
            self.log.error(err)


    def get_history(self)->DataFrame:
        try:
            return pd.read_csv(f"{self.data_dir}/{self.ticker}/data.csv", encoding='utf-8')
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


    def save_data(self, crypto: Crypto, stage: int):
        try:
            with open(f'{self.data_dir}/{self.ticker}/data.csv', 'a', encoding='utf-8') as handler:
                handler.write(f"\n{crypto.date}")
                handler.write(f",{crypto.close}")
                handler.write(f",{stage}")
                handler.write(f",{crypto.ema_short}")
                handler.write(f",{crypto.ema_middle}")
                handler.write(f",{crypto.ema_long}")
                handler.write(f",{crypto.signal}")
                handler.write(f",{crypto.histogram_upper}")
                handler.write(f",{crypto.histogram_middle}")
                handler.write(f",{crypto.histogram_lower}")
                handler.write(f",{crypto.macd_upper}")
                handler.write(f",{crypto.macd_middle}")
                handler.write(f",{crypto.macd_lower}")
                handler.write(f",{crypto.close_slope}")
                handler.write(f",{crypto.ema_short_slope}")
                handler.write(f",{crypto.ema_middle_slope}")
                handler.write(f",{crypto.ema_long_slope}")
                handler.write(f",{crypto.signal_slope}")
                handler.write(f",{crypto.macd_upper_slope}")
                handler.write(f",{crypto.macd_middle_slope}")
                handler.write(f",{crypto.macd_lower_slope}")
        except Exception as err:
            self.log.error(err)


