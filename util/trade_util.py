import os
from datetime import datetime
from typing import Union, Any

import pyupbit
from pyupbit import Upbit

from logger import get_logger
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

    def get_stage(self, data)-> int:
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

    def response_stage(self, stage:int)-> None:
        # 매수 검토
        if (stage == 4 or stage == 5 or stage == 6) and self.crypto_util.get_amount(self.ticker) == 0:
            msg = self.can_buy(stage)
            if msg["result"]:
                self.buy(msg["price"])
        # 매도 검토
        elif (stage == 1 or stage == 2 or stage == 3) and self.crypto_util.get_amount(self.ticker) != 0 and self.can_sell(stage) == True:
            self.sell()

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

    def compare_for_buy(self, key: str, n: int, index:int = 2) -> bool:
        try:
            data = self.crypto_util.get_history()
            for i in range(0, n):
                if not (data[key].iloc[-(i + 1)] > data[key].iloc[-(i + index)]):
                    return False
            return True
        except Exception as err:
            self.log.error(err)
            return False

    def compare_for_sell(self, key: str, n: int, index:int = 2) -> bool:
        try:
            data = self.crypto_util.get_history()
            for i in range(0, n):
                if not (data[key].iloc[-(i + 1)] < data[key].iloc[-(i + index)]):
                    return False
            return True
        except Exception as err:
            self.log.error(err)
            return False

    def can_buy(self, stage: int)->dict[str, Any]:
        data = {}
        try :
            if (stage == 4 and self.crypto_util.get_amount("KRW") > 6003 and len(
                    self.crypto_util.get_history()) > 5 and
                    (self.compare_for_buy("macd_upper", 4, 2) or self.compare_for_buy("macd_upper", 4, 3)) and
                    (self.compare_for_buy("macd_middle", 4, 2) or self.compare_for_buy("macd_middle", 4, 3)) and
                    (self.compare_for_buy("macd_lower", 4, 2) or self.compare_for_buy("macd_lower", 4, 3))):
                data["price"] = 6000
                data["result"] = True
            elif (stage == 5 and self.crypto_util.get_amount("KRW") > 7004 and len(
                    self.crypto_util.get_history()) > 5 and
                  (self.compare_for_buy("macd_upper", 5, 2) or self.compare_for_buy("macd_upper", 4, 3)) and
                  (self.compare_for_buy("macd_middle", 4, 2) or self.compare_for_buy("macd_middle", 4, 3)) and
                  (self.compare_for_buy("macd_lower", 4, 2) or self.compare_for_buy("macd_lower", 4, 3))):
                data["price"] = 7000
                data["result"] = True
            elif (stage == 6 and self.crypto_util.get_amount("KRW") > 8004 and len(
                    self.crypto_util.get_history()) > 5 and
                  (self.compare_for_buy("macd_upper", 5, 2) or self.compare_for_buy("macd_upper", 5, 3)) and
                  (self.compare_for_buy("macd_middle", 4, 2) or self.compare_for_buy("macd_middle", 4, 3)) and
                  (self.compare_for_buy("macd_lower", 4, 2) or self.compare_for_buy("macd_lower", 4, 3))):
                data["price"] = 8000
                data["result"] = True
            else:
                data["result"] = False
        except Exception as err:
            self.log.error(err)
            data["result"] = False
        return data

    def can_sell(self, stage: int):
        profit = (pyupbit.get_current_price(
            f"KRW-{self.ticker}") - self.crypto_util.get_my_price()) / self.crypto_util.get_my_price() * 100

        try :
            if (stage == 1  and len( self.crypto_util.get_history()) > 5 and profit > 0.8 and
                    (self.compare_for_sell("macd_upper", 3, 2) or self.compare_for_sell("macd_upper", 3, 3)) and
                    (self.compare_for_sell("macd_middle", 3, 2) or self.compare_for_sell("macd_middle", 2, 3)) and
                    (self.compare_for_sell("macd_lower", 3, 2) or self.compare_for_sell("macd_lower", 2, 3))):
                    return True
            elif (stage == 2 and len(self.crypto_util.get_history()) > 5 and profit > 0.8 and
                  (self.compare_for_sell("macd_upper", 4, 2) or self.compare_for_sell("macd_upper", 3, 3)) and
                  (self.compare_for_sell("macd_middle", 3, 2) or self.compare_for_sell("macd_middle", 3, 3)) and
                  (self.compare_for_sell("macd_lower", 3, 2) or self.compare_for_sell("macd_lower", 2, 3))):
                   return True
            elif (stage == 3  and len(self.crypto_util.get_history()) > 5 and profit > 0.8 and
                  (self.compare_for_sell("macd_upper", 4, 2) or self.compare_for_sell("macd_upper", 4, 3)) and
                  (self.compare_for_sell("macd_middle", 3, 2) or self.compare_for_sell("macd_middle", 3, 3)) and
                  (self.compare_for_sell("macd_lower", 3, 2) or self.compare_for_sell("macd_lower", 3, 3))):
                  return True
            else:
                return False
        except Exception as err:
            self.log.error(err)
            return False

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

