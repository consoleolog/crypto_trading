from typing import Union

import pyupbit

from pyupbit import Upbit

from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY
from logger import get_logger


class CryptoService:
    def __init__(self, ticker: str):
        self.UPBIT = Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        self.TICKER = ticker
        self.log = get_logger(ticker)

    def get_amount(self, ticker:str)-> Union[int, float]:
        try:
            balances = self.UPBIT.get_balances()
            for b in balances:
                if b['currency'] == ticker:
                    if b['balance'] is not None:
                        return float(b['balance'])
                    else:
                        return 0
            return 0
        except Exception as err:
            self.log.error(err)
            return 0

    def EMA(self, interval:str, count:int, ema_options: dict[str, int]):
        try:
            data = pyupbit.get_ohlcv(
                ticker=f"KRW-{self.TICKER}",
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

            data = data.reset_index()
            data.rename(columns={"index": "date"}, inplace=True)

            data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
            data.dropna(inplace=True)

            return data
        except Exception as err:
            self.log.error(err)
            raise Exception(err)