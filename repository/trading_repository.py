import os
from datetime import datetime

import pandas as pd

from logger import get_logger
from model.trade import Trade


class TradingRepository:
    def __init__(self, ticker):
        self.data_dir = f'{os.getcwd()}/data'
        self.TICKER = ticker
        self.log = get_logger(self.TICKER)

    def get_trade_history(self):
        data = pd.read_csv(f"{self.data_dir}/{self.TICKER}/buy.csv", encoding="utf-8")
        return data.iloc[-1]

    def create_file(self):
        if not os.path.exists(f"{self.data_dir}/{self.TICKER}/buy.csv"):
            self.log.debug(f"create {self.TICKER} csv files.....")
            with open(f"{self.data_dir}/{self.TICKER}/buy.csv", "w", encoding="utf-8") as f:
                f.write("date")
                f.write(",ticker")
                f.write(",my_price")
                f.write(",market_price")
                f.write(",balance")
                f.write(",reason")
                f.close()
        if not os.path.exists(f"{self.data_dir}/{self.TICKER}/buy_sell.csv"):
            with open(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", "w", encoding="utf-8") as f:
                f.write("date")
                f.write(",ticker")
                f.write(",buy/sell")
                f.write(",my_price")
                f.write(",market_price")
                f.write(",balance")
                f.write(",reason")
                f.close()

    def save(self, trade: Trade, code):
        datefmt = '%Y-%m-%d %H:%M:%S'

        dt = datetime.fromisoformat(trade.create_time)

        fdt = dt.strftime(datefmt)

        with open(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", "a", encoding="utf-8") as f:
            f.write(f"\n{fdt}")
            f.write(f",{trade.ticker}")
            f.write(f",{code}")
            f.write(f",{trade.price}")
            f.write(f",{trade.market_price}")
            f.write(f",{trade.balance}")

        if code == "BUY":
            with open(f"{self.data_dir}/{self.TICKER}/buy.csv","a", encoding="utf-8") as f:
                f.write(f"\n{fdt}")
                f.write(f",{trade.ticker}")
                f.write(f",{trade.price}")
                f.write(f",{trade.market_price}")
                f.write(f",{trade.balance}")

    def save_result(self, msg, code):
        datefmt = '%Y-%m-%d %H:%M:%S'

        dt = datetime.fromisoformat(msg['created_at'])

        fdt = dt.strftime(datefmt)

        with open(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", "a", encoding="utf-8") as f:
            f.write(f"\n{fdt}")
            f.write(f",{msg['market']}")
            f.write(f",{code}")
            f.write(f",{msg['locked']}")
            f.write(f",{msg['market_price']}")
            f.write(f",{msg['balance']}")

        if code == "BUY":
            with open(f"{self.data_dir}/{self.TICKER}/buy.csv","a", encoding="utf-8") as f:
                f.write(f"\n{fdt}")
                f.write(f",{msg['market']}")
                f.write(f",{msg['locked']}")
                f.write(f",{msg['market_price']}")
                f.write(f",{msg['balance']}")
