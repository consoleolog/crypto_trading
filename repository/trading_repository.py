import os
from datetime import datetime

from logger import get_logger


class TradingRepository:
    def __init__(self, ticker):
        self.data_dir = f'{os.getcwd()}/data'
        self.TICKER = ticker
        self.log = get_logger(f"{self.TICKER}")

    def create_file(self):
        if not os.path.exists(f"{self.data_dir}/{self.TICKER}_buy.csv"):
            self.log.debug(f"create {self.TICKER}_buy.csv file.....")
            with open(f"{self.data_dir}/{self.TICKER}_buy.csv", "w", encoding="utf-8") as f:
                f.write("date")
                f.write(",ticker")
                f.write(",my_price")
                f.write(",market_price")
                f.write(",balance")
                f.write(",reason")
                f.close()

        if not os.path.exists(f"{self.data_dir}/{self.TICKER}_buy_sell.csv"):
            self.log.debug(f"create {self.TICKER}_buy_sell.csv file.....")
            with open(f"{self.data_dir}/{self.TICKER}_buy_sell.csv", "w", encoding="utf-8") as f:
                f.write("date")
                f.write(",ticker")
                f.write(",buy/sell")
                f.write(",my_price")
                f.write(",market_price")
                f.write(",balance")
                f.write(",reason")
                f.close()


    def save_result(self, msg, code):
        datefmt = '%Y-%m-%d %H:%M:%S'

        dt = datetime.fromisoformat(msg['created_at'])

        fdt = dt.strftime(datefmt)

        with open(f"{self.data_dir}/{self.TICKER}_buy_sell.csv", "a", encoding="utf-8") as f:
            f.write(f"\n{fdt}")
            f.write(f",{code}")
            f.write(f",{msg['market']}")
            f.write(f",{msg['locked']}")
            f.write(f",{msg['market_price']}")
            f.write(f",{msg['balance']}")

        if code == "BUY":
            with open(f"{self.data_dir}/{self.TICKER}_buy.csv","a", encoding="utf-8") as f:
                f.write(f"\n{fdt}")
                f.write(f",{msg['market']}")
                f.write(f",{msg['locked']}")
                f.write(f",{msg['market_price']}")
                f.write(f",{msg['balance']}")
