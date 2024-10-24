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

    def predict_values(self, data, models:dict[str, LinearRegression]):

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

        result["upper"] = data["upper_result"].iloc[-1]
        result["middle"] = data["middle_result"].iloc[-1]
        result["lower"] = data["lower_result"].iloc[-1]

        self.crypto_util.save_predict_data(crypto, result)


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

            result["upper"] = data["upper_result"].iloc[-1]
            result["middle"] = data["middle_result"].iloc[-1]
            result["lower"] = data["lower_result"].iloc[-1]

            self.crypto_util.save_data(crypto, result)
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

    def compare_vale(self):
        crypto_data = pd.read_csv(f"{os.getcwd()}/data/{self.ticker}/data.csv", encoding='utf-8').tail(n=6)

        crypto_data["buy_upper_result"] = crypto_data["macd_upper"] > crypto_data["macd_upper"].shift(1)
        crypto_data["buy_middle_result"] = crypto_data["macd_middle"] > crypto_data["macd_middle"].shift(1)
        crypto_data["buy_lower_result"] = crypto_data["macd_lower"] > crypto_data["macd_lower"].shift(1)

        crypto_data["sell_upper_result"] = crypto_data["macd_upper"] < crypto_data["macd_upper"].shift(1)
        crypto_data["sell_middle_result"] = crypto_data["macd_middle"] < crypto_data["macd_middle"].shift(1)
        crypto_data["sell_lower_result"] = crypto_data["macd_lower"] < crypto_data["macd_lower"].shift(1)

        return crypto_data.tail(n=5)


    def response_stage(self, stage, models: dict[str, LinearRegression]):
        try:
            crypto_data = pd.read_csv(f"{os.getcwd()}/data/{self.ticker}/data.csv", encoding='utf-8')
            crypto_predict_data = pd.read_csv(f"{os.getcwd()}/data/{self.ticker}/predict_data.csv", encoding='utf-8')

            macd_upper, macd_middle, macd_lower = crypto_data["upper_result"], crypto_data["middle_result"], crypto_data[
                "lower_result"]
            predict_upper, predict_middle, predict_lower = crypto_predict_data["upper_result"], crypto_predict_data[
                "middle_result"], crypto_predict_data["lower_result"]

            data = {"result": "wait"}

            # self.log.debug(f"""
            #
            # 1.
            # upper  : {macd_upper.iloc[-1]}
            # middle : {macd_middle.iloc[-1]}
            # lower  : {macd_lower.iloc[-1]}
            #
            # 2.
            # upper  : {macd_upper.iloc[-2]}
            # middle : {macd_middle.iloc[-2]}
            # lower  : {macd_lower.iloc[-2]}
            #
            # 3.
            # upper  : {macd_upper.iloc[-3]}
            # middle : {macd_middle.iloc[-3]}
            # lower  : {macd_lower.iloc[-3]}
            #
            # """)

            if (stage == 1 or stage == 2 or stage == 3) and len(crypto_data) > 5:
                data["code"] = "sell"
                # 매도 검토
                if all([macd_upper.iloc[-1] == False , macd_upper.iloc[-2] == False, macd_upper.iloc[-3] == False]) and \
                        all([macd_middle.iloc[-1] == False, macd_middle.iloc[-2] == False, macd_middle.iloc[-3] == False]) and \
                        all([macd_lower.iloc[-1] == False , macd_lower.iloc[-2] == False]):
                    data["result"] = "sell"

            elif stage == 4 and len(crypto_data) > 5:
                data["code"] = "buy"
                # 매수 검토
                if all([macd_upper.iloc[-1] == True, macd_upper.iloc[-2] == True, macd_upper.iloc[-3] == True]) and \
                        all([macd_middle.iloc[-1] == True,  macd_middle.iloc[-2] == True, macd_middle.iloc[-3] == True, macd_middle.iloc[-4] == True]) and \
                        all([macd_lower.iloc[-1] == True , macd_lower.iloc[-2] == True]) and \
                        all([predict_upper.iloc[-1] == True , predict_upper.iloc[-2] == True,
                             predict_middle.iloc[-1] == True , predict_middle.iloc[-2] == True,
                             predict_lower.iloc[-1] == True,  predict_lower.iloc[-2] == True]):
                    data["result"] = "buy"
                    data["price"] = 6000

                # 매수 철회 검토
                elif all([macd_upper.iloc[-1] == False, macd_upper.iloc[-2] == False,  macd_upper.iloc[-3] == False]) and \
                        all([macd_middle.iloc[-1] == False, macd_middle.iloc[-2] == False, macd_middle.iloc[-3] == False]) and \
                        all([predict_upper.iloc[-1] == False, predict_upper.iloc[-2] == False,
                             predict_middle.iloc[-1] == False, predict_middle.iloc[-2] == False]):
                    data["result"] = "sell"

            elif stage == 5 and len(crypto_data) > 5:
                data["code"] = "buy"
                # 매수 검토
                if all([macd_upper.iloc[-1] == True, macd_upper.iloc[-2]== True,macd_upper.iloc[-3]== True, macd_upper.iloc[-4]== True]) and \
                        all([macd_middle.iloc[-1] == True, macd_middle.iloc[-2]== True, macd_middle.iloc[-3]== True, macd_middle.iloc[-4]== True]) and \
                        all([macd_lower.iloc[-1]== True, macd_lower.iloc[-2]== True,  macd_lower.iloc[-3]== True]) and \
                        all([predict_upper.iloc[-1] == True, predict_upper.iloc[-2]== True,
                             predict_middle.iloc[-1] == True, predict_middle.iloc[-2]== True,
                             predict_lower.iloc[-1] == True, predict_lower.iloc[-2]== True]):
                    data["result"] = "buy"
                    data["price"] = 7000

                # 매수 철회 검토
                elif all([macd_upper.iloc[-1] == False, macd_upper.iloc[-2] == False,  macd_upper.iloc[-3] == False]) and \
                        all([macd_middle.iloc[-1] == False, macd_middle.iloc[-2] == False, macd_middle.iloc[-3] == False]) and \
                        all([predict_upper.iloc[-1] == False, predict_upper.iloc[-2] == False, predict_middle.iloc[-1] == False, predict_middle.iloc[-2] == False]):
                    data["result"] = "sell"

            elif stage == 6 and len(crypto_data) > 5:
                data["code"] = "buy"
                # 매수 검토
                if all([macd_upper.iloc[-1] == True, macd_upper.iloc[-2]== True,  macd_upper.iloc[-3]== True, macd_upper.iloc[-4]== True]) and \
                        all([macd_middle.iloc[-1] == True, macd_middle.iloc[-2] == True, macd_middle.iloc[-3] == True, macd_middle.iloc[-4]== True]) and \
                        all([macd_lower.iloc[-1] == True, macd_lower.iloc[-2]== True, macd_lower.iloc[-3] == True, macd_lower.iloc[-4]== True]) and \
                        all([predict_upper.iloc[-1] == True, predict_upper.iloc[-2]== True,
                             predict_middle.iloc[-1] == True, predict_middle.iloc[-2]== True,
                             predict_lower.iloc[-1] == True,predict_lower.iloc[-2]== True]):
                    data["result"] = "buy"
                    data["price"] = 8000

                # 매수 철회 검토
                elif all([macd_upper.iloc[-1] == False, macd_upper.iloc[-2] == False,  macd_upper.iloc[-3] == False]) and \
                        all([macd_middle.iloc[-1] == False, macd_middle.iloc[-2] == False, macd_middle.iloc[-3] == False]) and \
                        all([predict_upper.iloc[-1] == False, predict_upper.iloc[-2] == False, predict_middle.iloc[-1] == False, predict_middle.iloc[-2] == False]):
                    data["result"] = "sell"

            # 매수 신호
            if data["result"] == "buy" and self.crypto_util.get_amount(self.ticker) == 0:
                # self.buy(data["price"])
                self.log.debug(f" {self.ticker} 매수 신호 ")
            # 매도 신호
            elif data["result"] == "sell" and self.crypto_util.get_amount(self.ticker) != 0:

                upper1 = int(models["macd_upper"].predict([[ crypto_predict_data["macd_middle"].iloc[-1] ]]))

                middle1 = int(models["macd_middle"].predict([[crypto_predict_data["macd_upper"].iloc[-1]]])[0])
                middle2 = int(models["macd_middle"].predict([[ upper1 ]])[0])

                lower1 = int(models["macd_lower"].predict([[ crypto_predict_data["macd_middle"].iloc[-1] ]])[0])
                lower2 = int(models["macd_lower"].predict([[ middle1 ]])[0])

                upper2 = int(models["macd_upper"].predict([[ middle1 ]]))

                middle3 = int(models["macd_middle"].predict([[ upper2 ]])[0])
                lower3 = int(models["macd_lower"].predict([[ middle2 ]])[0])
                lower4 = int(models["macd_lower"].predict([[ middle3 ]])[0])

                # self.log.debug(f"""
                # Predict Values
                #
                # New
                #
                #
                # Old
                # upper  : {crypto_predict_data["macd_upper"].iloc[-1]}
                # middle : {crypto_predict_data["macd_middle"].iloc[-1]}
                # lower  : {crypto_predict_data["macd_lower"].iloc[-1]}
                #
                # """)

                # 매수 철회일 때
                if data["code"] == "buy":
                    if all([middle1 < crypto_predict_data["macd_middle"].iloc[-1],
                            middle2 < middle1,
                            middle3 < middle2,
                            lower4 < lower3,]):
                        # self.sell()
                        self.log.debug(f" {self.ticker} 매수 철회 신호")
                # 그냥 매도 신호일 때
                else:
                    if self.crypto_util.get_current_profit() > 0.1 or \
                            all([ middle1 < crypto_predict_data["macd_middle"].iloc[-1],
                                  middle2 < middle1,
                                  lower1 < crypto_predict_data["macd_lower"].iloc[-1],
                                  lower2 < lower1]):
                        # self.sell()
                        self.log.debug(f" {self.ticker} 매도 신호")

        except Exception as err:
            self.log.error(err)



