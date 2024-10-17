import os

import pandas as pd

from model.crypto import Crypto


class CryptoRepository:
    def __init__(self, ticker):
        self.data_dir = f'{os.getcwd()}/data'
        self.TICKER = ticker

    def get_history(self):
        return pd.read_csv(f"{self.data_dir}/{self.TICKER}/data.csv", encoding='utf-8')

    def create_file(self):
        if not os.path.exists(f"{self.data_dir}/{self.TICKER}/data.csv"):
            with open(f"{self.data_dir}/{self.TICKER}/data.csv", "w", encoding="utf-8") as f:
                f.write("date")
                f.write(",close")
                f.write(",stage")
                f.write(",ema_short")
                f.write(",ema_middle")
                f.write(",ema_long")
                f.write(",macd_short")
                f.write(",macd_middle")
                f.write(",macd_long")
                f.write(",close_slope")
                f.write(",ema_short_slope")
                f.write(",ema_middle_slope")
                f.write(",ema_long_slope")
                f.write(",macd_short_slope")
                f.write(",macd_middle_slope")
                f.write(",macd_long_slope")
                f.close()

    def save(self, crypto: Crypto, stage):
        with open(f'{self.data_dir}/{self.TICKER}/data.csv', 'a', encoding='utf-8') as f:
            f.write(f"\n{crypto.date}")
            f.write(f",{crypto.close}")
            f.write(f",{stage}")
            f.write(f",{crypto.ema_short}")
            f.write(f",{crypto.ema_middle}")
            f.write(f",{crypto.ema_long}")
            f.write(f",{crypto.macd_short}")
            f.write(f",{crypto.macd_middle}")
            f.write(f",{crypto.macd_long}")
            f.write(f",{crypto.close_slope}")
            f.write(f",{crypto.ema_short_slope}")
            f.write(f",{crypto.ema_middle_slope}")
            f.write(f",{crypto.ema_long_slope}")
            f.write(f",{crypto.macd_short_slope}")
            f.write(f",{crypto.macd_middle_slope}")
            f.write(f",{crypto.macd_long_slope}")

    def save_data(self, data, stage):

        with open(f'{self.data_dir}/{self.TICKER}/data.csv', 'a', encoding='utf-8') as f:
            f.write(f"\n{data['date'].iloc[-1]}")
            f.write(f",{data['close'].iloc[-1]}")
            f.write(f",{stage}")
            f.write(f",{data['ema_short'].iloc[-1]}")
            f.write(f",{data['ema_middle'].iloc[-1]}")
            f.write(f",{data['ema_long'].iloc[-1]}")
            f.write(f",{data['macd_short'].iloc[-1]}")
            f.write(f",{data['macd_middle'].iloc[-1]}")
            f.write(f",{data['macd_long'].iloc[-1]}")
            f.write(f",{data['close_slope'].iloc[-1]}")
            f.write(f",{data['ema_short_slope'].iloc[-1]}")
            f.write(f",{data['ema_middle_slope'].iloc[-1]}")
            f.write(f",{data['ema_long_slope'].iloc[-1]}")
            f.write(f",{data['macd_short_slope'].iloc[-1]}")
            f.write(f",{data['macd_middle_slope'].iloc[-1]}")
            f.write(f",{data['macd_long_slope'].iloc[-1]}")