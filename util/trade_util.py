import os
from datetime import datetime

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

    def get_stage(self, data, model:LinearRegression)-> int:
        predict_val = model.predict([ [data["macd_middle"].iloc[-2]] ])[0]
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

            self.crypto_util.save_data(crypto, predict_val ,result["stage"])
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

    def response_stage(self, stage, model: LinearRegression):
        try:
            history = self.crypto_util.get_history()
            macd_upper, macd_middle, macd_lower = history["macd_upper"], history["macd_middle"], history["macd_lower"]

            data = {"result": "wait"}

            if len(self.crypto_util.get_history()) > 1:
                predict_values = model.predict([[macd_middle.iloc[-1]],[macd_middle.iloc[-2]]])

                self.log.info(predict_values)

                if predict_values[0] > predict_values[1]:
                    data["predict"] = "buy"
                else:
                    data["predict"] = "sell"


            if (stage == 1 or stage == 2 or stage == 3) and len(self.crypto_util.get_history()) > 5:
                data["code"] = "sell"
                # 매도 검토
                if (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                        macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3] and
                        macd_lower.iloc[-1] < macd_lower.iloc[-2]):
                    data["result"] = "sell"

            elif stage == 4 and len(self.crypto_util.get_history()) > 5:
                data["code"] = "buy"

                # 매수 검토
                if (macd_upper.iloc[-1] > macd_upper.iloc[-2] > macd_upper.iloc[-3] and
                        macd_middle.iloc[-1] > macd_middle.iloc[-2] > macd_middle.iloc[-3] > macd_middle.iloc[-4] and
                        macd_lower.iloc[-1] > macd_lower.iloc[-2]):
                    data["result"] = "buy"
                    data["price"] = 8000

                # 매수 철회 검토
                elif (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                      macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3]):
                    data["result"] = "sell"

            elif stage == 5 and len(self.crypto_util.get_history()) > 5:
                data["code"] = "buy"

                # 매수 검토
                if (macd_upper.iloc[-1] > macd_upper.iloc[-2] > macd_upper.iloc[-3] > macd_upper.iloc[-4] and
                        macd_middle.iloc[-1] > macd_middle.iloc[-2] > macd_middle.iloc[-3] > macd_middle.iloc[-4] and
                        macd_lower.iloc[-1] > macd_lower.iloc[-2] > macd_lower.iloc[-3] ):
                    data["result"] = "buy"
                    data["price"] = 9000

                # 매수 철회 검토
                elif (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                      macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3]
                      ):
                    data["result"] = "sell"

            elif stage == 6 and len(self.crypto_util.get_history()) > 5:
                data["code"] = "buy"

                # 매수 검토
                if (macd_upper.iloc[-1] > macd_upper.iloc[-2] > macd_upper.iloc[-3] > macd_upper.iloc[-4] and
                        macd_middle.iloc[-1] > macd_middle.iloc[-2] > macd_middle.iloc[-3] > macd_middle.iloc[-4] and
                        macd_lower.iloc[-1] > macd_lower.iloc[-2] > macd_lower.iloc[-3] > macd_lower.iloc[-4]):
                    data["result"] = "buy"
                    data["price"] = 10000

                # 매수 철회 검토
                elif (macd_upper.iloc[-1] < macd_upper.iloc[-2] < macd_upper.iloc[-3] and
                      macd_middle.iloc[-1] < macd_middle.iloc[-2] < macd_middle.iloc[-3]
                      ):
                    data["result"] = "sell"

            # 매수 신호
            if data["result"] == "buy" and self.crypto_util.get_amount(self.ticker) == 0:
                # self.buy(data["price"])
                pass
            # 매도 신호
            elif data["result"] == "sell" and self.crypto_util.get_amount(self.ticker) != 0:
                # 매수 철회 일 때
                if data["code"] == "buy" and data["predict"] == "sell":
                    # self.sell()
                    pass
                # 그냥 매도 신호 일 때
                else:
                    if self.crypto_util.get_current_profit() > 0.7:
                        # self.sell()
                        pass

        except Exception as err:
            self.log.error(err)
