import os
from datetime import datetime

import pandas as pd
import pyupbit
from pyupbit import Upbit
from sklearn.linear_model import LinearRegression

from config import get_logger
from model.crypto import Crypto
from model.trade import Trade
from util.common_util import CommonUtil
from util.crypto_util import CryptoUtil


class TradeUtil:
    def __init__(self,
                 upbit:Upbit,
                 ticker:str,
                 crypto_util:CryptoUtil,
                 common_util:CommonUtil,):
        self.crypto_util = crypto_util
        self.common_util = common_util
        self.ticker = ticker
        self.upbit = upbit
        self.log = get_logger(ticker)
        self.crypto_data = pd.read_csv(f"{os.getcwd()}/data/{self.ticker}/data.csv", encoding='utf-8')
        self.crypto_predict_data = pd.read_csv(f"{os.getcwd()}/data/{self.ticker}/predict_data.csv", encoding='utf-8')

    def predict_values(self, data, models):

        result = {}

        ema_short = int(models["ema_short"].predict([ [data["ema_middle"].iloc[-1]] ])[0])
        ema_middle = int(models["ema_middle"].predict([ [data["ema_short"].iloc[-1]] ])[0])
        ema_long = int(models["ema_long"].predict([ [data["ema_middle"].iloc[-1]] ])[0])

        macd_upper = int(models["macd_upper"].predict([ [data["macd_middle"].iloc[-1]] ])[0])
        macd_middle = int(models["macd_middle"].predict([ [data["macd_upper"].iloc[-1]] ])[0])
        macd_lower = int(models["macd_lower"].predict([ [data["macd_middle"].iloc[-1]] ])[0])

        if ema_short >= ema_middle >= ema_long:
            result["stage"] = 1
        # 중기 > 단기 > 장기
        elif ema_middle >= ema_short >= ema_long:
            result["stage"] = 2
        # 중기 > 장기 > 단기
        elif ema_middle >= ema_long >= ema_short:
            result["stage"] = 3
        # 장기 > 중기 > 단기
        elif ema_long >= ema_middle >= ema_short:
            result["stage"] = 4
        # 장기 > 단기 > 중기
        elif ema_long >= ema_short >= ema_middle:
            result["stage"] = 5
        # 단기 > 장기 > 중기
        elif ema_short >= ema_long >= ema_middle:
            result["stage"] = 6

        create_df = {
            "date": [data["date"].iloc[-1]],
            "close":[data["close"].iloc[-1]],
            "ema_short": [ema_short],
            "ema_middle": [ema_middle],
            "ema_long": [ema_long],
            "macd_upper": [macd_upper],
            "macd_middle": [macd_middle],
            "macd_lower": [macd_lower],
        }

        create_crypto = pd.DataFrame(create_df)

        crypto = Crypto(create_crypto)

        self.crypto_util.save_predict_data(crypto, result["stage"])


    def get_stage(self, data, models)-> int:

        self.predict_values(data, models)

        result = {}
        try:
            crypto = Crypto(data)
            # 단기 > 중기 > 장기
            if crypto.ema_short >= crypto.ema_middle >= crypto.ema_long:
                result["stage"] = 1
            # 중기 > 단기 > 장기
            elif crypto.ema_middle >= crypto.ema_short >= crypto.ema_long:
                result["stage"] = 2
            # 중기 > 장기 > 단기
            elif crypto.ema_middle >= crypto.ema_long >= crypto.ema_short:
                result["stage"] = 3
            # 장기 > 중기 > 단기
            elif crypto.ema_long >= crypto.ema_middle >= crypto.ema_short:
                result["stage"] = 4
            # 장기 > 단기 > 중기
            elif crypto.ema_long >= crypto.ema_short >= crypto.ema_middle:
                result["stage"] = 5
            # 단기 > 장기 > 중기
            elif crypto.ema_short >= crypto.ema_long >= crypto.ema_middle:
                result["stage"] = 6


            self.crypto_util.save_data(crypto, result["stage"])
            return result["stage"]
        except Exception as err:
            self.log.error(err)

    def buy(self, price: int) -> None:
        try:
            msg = self.upbit.buy_market_order(f"KRW-{self.ticker}", price)
            if isinstance(msg, dict):
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.ticker}")
                self.log.debug(f"sending {self.ticker} mail :: buy result ....")
                self.save_result(Trade(msg), "BUY")
                self.common_util.send_mail({
                    "content":f"{self.ticker} 매수 결과 보고",
                    "filename":"buy_sell.csv"
                })
        except Exception as e:
            self.log.error(e)

    def sell(self) -> None:
        try:
            msg = self.upbit.sell_market_order(f"KRW-{self.ticker}", self.crypto_util.get_amount(self.ticker))
            if isinstance(msg, dict):
                self.log.debug(f"sending {self.ticker} mail :: sell result ....")
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.ticker}")
                msg['locked'] = 0
                self.save_result(Trade(msg), "SELL")
                self.common_util.send_mail({
                    "content": f"{self.ticker} 매도 결과 보고",
                    "filename": "buy_sell.csv"
                })
        except Exception as error:
            self.log.error(error)

    def save_result(self, trade: Trade, code: str)->None:
        try:
            datefmt = '%Y-%m-%d %H:%M:%S'
            dt = datetime.fromisoformat(trade.create_time)
            fdt = dt.strftime(datefmt)

            with open(f"{os.getcwd()}/data/{self.ticker}/buy_sell.csv", "a", encoding="utf-8") as handler:
                handler.write(f"\n{fdt}")
                handler.write(f",{trade.ticker}")
                handler.write(f",{code}")
                handler.write(f",{trade.price}")
                handler.write(f",{trade.market_price}")
        except Exception as err:
            self.log.error(err)

    def response_stage(self, stage):
        try:
            macd_upper, macd_middle, macd_lower = self.crypto_data["macd_upper"], self.crypto_data["macd_middle"], self.crypto_data["macd_lower"]
            predict_upper, predict_middle, predict_lower = self.crypto_predict_data["macd_upper"], self.crypto_predict_data["macd_middle"], self.crypto_predict_data["macd_lower"]

            data = {"result": "wait"}

            if (stage == 1 or stage == 2 or stage == 3) and len(self.crypto_data) > 5:
                data["code"] = "sell"
                # 매도 검토
                if (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                        macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3] and
                        macd_lower.iloc[-1] < macd_lower.iloc[-2]):
                    data["result"] = "sell"

            elif stage == 4 and len(self.crypto_data) > 5:
                data["code"] = "buy"

                # 매수 검토
                if (macd_upper.iloc[-1] > macd_upper.iloc[-2] > macd_upper.iloc[-3] and
                        macd_middle.iloc[-1] > macd_middle.iloc[-2] > macd_middle.iloc[-3] > macd_middle.iloc[-4] and
                        macd_lower.iloc[-1] > macd_lower.iloc[-2] and
                    predict_upper.iloc[-1] > predict_upper.iloc[-2] and
                    predict_middle.iloc[-1] > predict_middle.iloc[-2] and
                    predict_lower.iloc[-1] > predict_lower.iloc[-2]):
                    data["result"] = "buy"
                    data["price"] = 8000

                # 매수 철회 검토
                elif (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                      macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3] and
                      predict_upper.iloc[-1] < predict_upper.iloc[-2] and
                      predict_middle.iloc[-1] < predict_middle.iloc[-2]):
                    data["result"] = "sell"

            elif stage == 5 and len(self.crypto_data) > 5:
                data["code"] = "buy"

                # 매수 검토
                if (macd_upper.iloc[-1] > macd_upper.iloc[-2] > macd_upper.iloc[-3] > macd_upper.iloc[-4] and
                        macd_middle.iloc[-1] > macd_middle.iloc[-2] > macd_middle.iloc[-3] > macd_middle.iloc[-4] and
                        macd_lower.iloc[-1] > macd_lower.iloc[-2] > macd_lower.iloc[-3] and
                        predict_upper.iloc[-1] > predict_upper.iloc[-2] and
                        predict_middle.iloc[-1] > predict_middle.iloc[-2] and
                        predict_lower.iloc[-1] > predict_lower.iloc[-2]):
                    data["result"] = "buy"
                    data["price"] = 9000

                # 매수 철회 검토
                elif (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                      macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3] and
                      predict_upper.iloc[-1] < predict_upper.iloc[-2] and
                      predict_middle.iloc[-1] < predict_middle.iloc[-2]):
                    data["result"] = "sell"

            elif stage == 6 and len(self.crypto_data) > 5:
                data["code"] = "buy"

                # 매수 검토
                if (macd_upper.iloc[-1] > macd_upper.iloc[-2] > macd_upper.iloc[-3] > macd_upper.iloc[-4] and
                        macd_middle.iloc[-1] > macd_middle.iloc[-2] > macd_middle.iloc[-3] > macd_middle.iloc[-4] and
                        macd_lower.iloc[-1] > macd_lower.iloc[-2] > macd_lower.iloc[-3] > macd_lower.iloc[-4] and
                    predict_upper.iloc[-1] > predict_upper.iloc[-2] and
                    predict_middle.iloc[-1] > predict_middle.iloc[-2] and
                    predict_lower.iloc[-1] > predict_lower.iloc[-2]):
                    data["result"] = "buy"
                    data["price"] = 10000

                # 매수 철회 검토
                elif (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                      macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3] and
                      predict_upper.iloc[-1] < predict_upper.iloc[-2] and
                      predict_middle.iloc[-1] < predict_middle.iloc[-2]):
                    data["result"] = "sell"

            # 매수 신호
            if data["result"] == "buy" and self.crypto_util.get_amount(self.ticker) == 0:
                # self.buy(data["price"])
                pass
            # 매도 신호
            elif data["result"] == "sell" and self.crypto_util.get_amount(self.ticker) != 0:
                # 매수 철회 일 때
                if data["code"] == "buy":
                    # self.sell()
                    pass
                # 그냥 매도 신호 일 때
                else:
                    if self.crypto_util.get_current_profit() > 0.7:
                        # self.sell()
                        pass

        except Exception as err:
            self.log.error(err)



