import os
import time

import numpy as np
import pyupbit
from sklearn.linear_model import LinearRegression


class CryptoCurrencyUtil:

    @staticmethod
    def get_ema(data, opt):
        data["ema_short"] = data["close"].ewm(span=opt["short"]).mean()
        data["ema_middle"] = data["close"].ewm(span=opt["middle"]).mean()
        data["ema_long"] = data["close"].ewm(span=opt["long"]).mean()
        return data

    @staticmethod
    def get_macd(data):
        data["macd_upper"] = data["ema_short"] - data["ema_middle"]  # (상)
        data["macd_middle"] = data["ema_short"] - data["ema_long"]  # (중)
        data["macd_lower"] = data["ema_middle"] - data["ema_long"]  # (하)
        data["upper_result"] = data["macd_upper"] > data["macd_upper"].shift(1)
        data["middle_result"] = data["macd_middle"] > data["macd_middle"].shift(1)
        data["lower_result"] = data["macd_lower"] > data["macd_lower"].shift(1)
        return data

    @staticmethod
    def get_stage(data):
        short, middle, long = data["ema_short"], data["ema_middle"], data["ema_long"]
        if short >= middle >= long:
            return 1
            # 중기 > 단기 > 장기
        elif middle >= short >= long:
            return 2
            # 중기 > 장기 > 단기
        elif middle >= long >= short:
            return 3
            # 장기 > 중기 > 단기
        elif long >= middle >= short:
            return 4
            # 장기 > 단기 > 중기
        elif long >= short >= middle:
            return 5
            # 단기 > 장기 > 중기
        elif short >= long >= middle:
            return 6

    @staticmethod
    def create_data_dir():
        if not os.path.exists(f"{os.getcwd()}/data"):
            os.mkdir(f"{os.getcwd()}/data")

    @staticmethod
    def get_ticker_list():
        tickers = []
        for i, data in enumerate(pyupbit.get_tickers(fiat="KRW")):
            try:
                df = pyupbit.get_ohlcv(data, "minutes1", 1000)
                df.reset_index()
                df2 = pyupbit.get_ohlcv(data, "minutes1", 120)
                df2.reset_index()
                tickers.append(data.replace("KRW-", ""))
            except AttributeError:
                pass
            time.sleep(1)
        return tickers

    @staticmethod
    def coin_validation(ticker):
        try:
            df = pyupbit.get_ohlcv(f"KRW-{ticker}", "minutes", 1000)
            data = CryptoCurrencyUtil.get_macd(
                CryptoCurrencyUtil.get_ema(df, {
                    "short": 10,
                    "middle": 20,
                    "long": 60,
                })
            )
            ma_short, ma_middle, ma_long = (np.array(data["ema_short"]),
                                            np.array(data["ema_middle"]),
                                            np.array(data["ema_long"]))

            macd_up, macd_middle, macd_low = (np.array(data["macd_upper"]),
                                              np.array(data["macd_middle"]),
                                              np.array(data["macd_lower"]))

            MaShortModel = LinearRegression().fit(ma_middle.reshape((-1, 1)), ma_short)

            MaMiddleModel = LinearRegression().fit(ma_short.reshape((-1, 1)), ma_middle)

            MaLongModel = LinearRegression().fit(ma_middle.reshape((-1, 1)), ma_long)

            MACDUpperModel = LinearRegression().fit(macd_middle.reshape((-1, 1)), macd_up)

            MACDMiddleModel = LinearRegression().fit(macd_up.reshape((-1, 1)), macd_middle)

            MACDLowerModel = LinearRegression().fit(macd_middle.reshape((-1, 1)), macd_low)

            return {
                "ema": {
                    "short": MaShortModel.score(ma_middle.reshape((-1, 1)), ma_short),
                    "middle": MaMiddleModel.score(ma_short.reshape((-1, 1)), ma_middle),
                    "long": MaLongModel.score(ma_middle.reshape((-1, 1)), ma_long)
                },
                "macd": {
                    "upper": MACDUpperModel.score(macd_middle.reshape((-1, 1)), macd_up),
                    "middle": MACDMiddleModel.score(macd_up.reshape((-1, 1)), macd_middle),
                    "lower": MACDLowerModel.score(macd_middle.reshape((-1, 1)), macd_low)
                }
            }
        except TypeError:
            pass

