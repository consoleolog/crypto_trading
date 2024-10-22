import os
from datetime import datetime
from typing import Union

import pandas as pd

from logger import get_logger
from model.trade import Trade


class TradingRepository:
    def __init__(self, ticker: str):
        self.data_dir = f'{os.getcwd()}/data'
        self.TICKER = ticker
        self.log = get_logger(ticker)

    def get_my_price(self) -> Union[int, float]:
        price = 0
        count = 0
        try:
            df = pd.read_csv(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", encoding="utf-8")
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

    def create_file(self)->type(None):
        try:
            if not os.path.exists(f"{self.data_dir}/{self.TICKER}/buy_sell.csv"):
                with open(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", "w", encoding="utf-8") as handler:
                    handler.write("date")
                    handler.write(",ticker")
                    handler.write(",buy/sell")
                    handler.write(",my_price")
                    handler.write(",market_price")

            if not os.path.exists(f"{self.data_dir}/{self.TICKER}/data.csv"):
                with open(f"{self.data_dir}/{self.TICKER}/data.csv", "w", encoding="utf-8") as handler:
                    handler.write("date")
                    handler.write(",close")
                    handler.write(",stage")
                    handler.write(",ema_short")
                    handler.write(",ema_middle")
                    handler.write(",ema_long")
                    handler.write(",signal")
                    handler.write(",histogram_upper")
                    handler.write(",histogram_middle")
                    handler.write(",histogram_lower")
                    handler.write(",macd_upper")
                    handler.write(",macd_middle")
                    handler.write(",macd_lower")
                    handler.write(",close_slope")
                    handler.write(",ema_short_slope")
                    handler.write(",ema_middle_slope")
                    handler.write(",ema_long_slope")
                    handler.write(",signal_slope")
                    handler.write(",macd_upper_slope")
                    handler.write(",macd_middle_slope")
                    handler.write(",macd_lower_slope")
        except Exception as err:
            self.log.error(err)
            raise Exception(err)


    def save(self, trade: Trade, code: str)->type(None):
        try:
            datefmt = '%Y-%m-%d %H:%M:%S'

            dt = datetime.fromisoformat(trade.create_time)

            fdt = dt.strftime(datefmt)

            with open(f"{self.data_dir}/{self.TICKER}/buy_sell.csv", "a", encoding="utf-8") as handler:
                handler.write(f"\n{fdt}")
                handler.write(f",{trade.ticker}")
                handler.write(f",{code}")
                handler.write(f",{trade.price}")
                handler.write(f",{trade.market_price}")
        except Exception as err:
            self.log.error(err)
            pass
