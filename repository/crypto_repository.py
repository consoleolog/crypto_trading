import os

import pandas as pd
from pandas import DataFrame

from logger import get_logger
from model.crypto import Crypto


class CryptoRepository:
    def __init__(self, ticker: str):
        self.data_dir = f'{os.getcwd()}/data'
        self.TICKER = ticker
        self.log = get_logger(ticker)

    def get_history(self) -> DataFrame:
        try:
            return pd.read_csv(f"{self.data_dir}/{self.TICKER}/data.csv", encoding='utf-8')
        except Exception as err:
            self.log.error(err)
            pass

    def save(self, crypto: Crypto, stage: int):
        try:
            with open(f'{self.data_dir}/{self.TICKER}/data.csv', 'a', encoding='utf-8') as handler:
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
            pass