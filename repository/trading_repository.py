import os
from datetime import datetime

import pandas as pd
from pandas import DataFrame

from logger import get_logger
from model.trade import Trade


class TradingRepository:
    def __init__(self, ticker: str):
        self.data_dir = f'{os.getcwd()}/data'
        self.TICKER = ticker
        self.log = get_logger(self.TICKER)

    def get_trade_history(self)->DataFrame:
        data = pd.read_csv(f"{self.data_dir}/{self.TICKER}/buy.csv", encoding="utf-8")
        return data.iloc[-1]

    def create_file(self)->type(None):
        if not os.path.exists(f"{self.data_dir}/{self.TICKER}/buy.csv"):
            self.log.debug(f"create {self.TICKER} csv files.....")
            with open(f"{self.data_dir}/{self.TICKER}/buy.csv", "w", encoding="utf-8") as handler:
                handler.write("date")
                handler.write(",ticker")
                handler.write(",my_price")
                handler.write(",market_price")

        if not os.path.exists(f"{self.data_dir}/{self.TICKER}/buy_sell.csv"):
            with open(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", "w", encoding="utf-8") as handler:
                handler.write("date")
                handler.write(",ticker")
                handler.write(",buy/sell")
                handler.write(",my_price")
                handler.write(",market_price")


    def save(self, trade: Trade, code: str)->type(None):
        datefmt = '%Y-%m-%d %H:%M:%S'

        dt = datetime.fromisoformat(trade.create_time)

        fdt = dt.strftime(datefmt)

        with open(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", "a", encoding="utf-8") as handler:
            handler.write(f"\n{fdt}")
            handler.write(f",{trade.ticker}")
            handler.write(f",{code}")
            handler.write(f",{trade.price}")
            handler.write(f",{trade.market_price}")

        if code == "BUY":
            with open(f"{self.data_dir}/{self.TICKER}/buy.csv","a", encoding="utf-8") as handler:
                handler.write(f"\n{fdt}")
                handler.write(f",{trade.ticker}")
                handler.write(f",{trade.price}")
                handler.write(f",{trade.market_price}")
