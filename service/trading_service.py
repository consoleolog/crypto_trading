import os.path

import pyupbit
from pyupbit import Upbit

from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY
from logger import get_logger
from model.crypto import Crypto
from model.trade import Trade
from repository.crypto_repository import CryptoRepository
from repository.trading_repository import TradingRepository
from service.crypto_service import CryptoService
from service.mail_service import MailService


class TradingService:
    def __init__(self, ticker:str,
                       crypto_repository: CryptoRepository,
                       trading_repository: TradingRepository,
                       mail_service: MailService,
                       crypto_service: CryptoService,):
        self.TICKER = ticker
        self.UPBIT = Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        self.cryptoRepository = crypto_repository
        self.tradingRepository = trading_repository
        self.mailService = mail_service
        self.cryptoService = crypto_service
        self.log = get_logger(self.TICKER)

    def get_stage(self, data)-> int:
        try:
            data['close_slope'] = data['close'].diff()
            data['ema_short_slope'] = data['ema_short'].diff()
            data['ema_middle_slope'] = data['ema_middle'].diff()
            data['ema_long_slope'] = data['ema_long'].diff()
            data['signal_slope'] = data['signal'].diff()
            data['histogram_upper'] = data['macd_upper'] - data['signal']
            data['histogram_middle'] = data['macd_middle'] - data['signal']
            data['histogram_lower'] = data['macd_lower'] - data['signal']

            result = {}

            # 단기 > 중기 > 장기
            if data["ema_short"].iloc[-1] >= data["ema_middle"].iloc[-1] >= data["ema_long"].iloc[-1]:
                result["stage"] = 1
            # 중기 > 단기 > 장기
            elif data["ema_middle"].iloc[-1] >= data["ema_short"].iloc[-1] >= data["ema_long"].iloc[-1]:
                result["stage"] = 2
            # 중기 > 장기 > 단기
            elif data["ema_middle"].iloc[-1] >= data["ema_long"].iloc[-1] >= data["ema_short"].iloc[-1]:
                result["stage"] = 3
            # 장기 > 중기 > 단기
            elif data["ema_long"].iloc[-1] >= data["ema_middle"].iloc[-1] >= data["ema_short"].iloc[-1]:
                result["stage"] = 4
            # 장기 > 단기 > 중기
            elif data["ema_long"].iloc[-1] >= data["ema_short"].iloc[-1] >= data["ema_middle"].iloc[-1]:
                result["stage"] = 5
            # 단기 > 장기 > 중기
            elif data["ema_short"].iloc[-1] >= data["ema_long"].iloc[-1] >= data["ema_middle"].iloc[-1]:
                result["stage"] = 6

            self.cryptoRepository.save(Crypto(data), result["stage"])
            return result["stage"]
        except Exception as err:
            self.log.error(err)
            pass

    def BUY(self, price: int) -> type(None):
        try:
            msg = self.UPBIT.buy_market_order(f"KRW-{self.TICKER}", price)
            if isinstance(msg, dict):
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.TICKER}")
                self.log.debug(f"sending {self.TICKER} mail :: buy result ....")
                self.tradingRepository.save(Trade(msg), "BUY")
                self.mailService.send_file({
                    "content":f"{self.TICKER} 매수 결과 보고",
                    "filename":"buy_sell.csv"
                })
        except Exception as e:
            self.log.error(e)
            pass

    def SELL(self) -> type(None):
        try:
            msg = self.UPBIT.sell_market_order(f"KRW-{self.TICKER}", self.cryptoService.get_amount(self.TICKER))
            if isinstance(msg, dict):
                self.log.debug(f"sending {self.TICKER} mail :: sell result ....")
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.TICKER}")
                msg['locked'] = 0
                self.tradingRepository.save(Trade(msg), "SELL")
                self.mailService.send_file({
                    "content": f"{self.TICKER} 매도 결과 보고",
                    "filename": "buy_sell.csv"
                })
        except Exception as error:
            self.log.error(error)
            pass

    def init(self) -> type(None):
        try:
            if not os.path.exists(f"{os.getcwd()}/data"):
                os.mkdir(f"{os.getcwd()}/data")

            if not os.path.exists(f"{os.getcwd()}/data/{self.TICKER}"):
                os.mkdir(f"{os.getcwd()}/data/{self.TICKER}")

            self.log.debug(f"create {self.TICKER} csv files.....")
            self.tradingRepository.create_file()
        except Exception as err:
            raise Exception(err)

    def compare_for_buy(self, key: str, n: int, index:int = 2) -> bool:
        try:
            data = self.cryptoRepository.get_history()
            for i in range(0, n):
                if not (data[key].iloc[-(i + 1)] >= data[key].iloc[-(i + index)]):
                    return False
            return True
        except Exception as err:
            self.log.error(err)
            return False

    def compare_for_sell(self, key: str, n: int, index:int = 2) -> bool:
        try:
            data = self.cryptoRepository.get_history()
            for i in range(0, n):
                if not (data[key].iloc[-(i + 1)] <= data[key].iloc[-(i + index)]):
                    return False
            return True
        except Exception as err:
            self.log.error(err)
            return False

    def can_buy(self, stage: int):
        data = {}
        try :
            if (stage == 4 and self.cryptoService.get_amount("KRW") > 6003 and len(
                    self.cryptoRepository.get_history()) > 5 and
                    (self.compare_for_buy("macd_upper", 4, 2) or self.compare_for_buy("macd_upper", 4, 3)) and
                    (self.compare_for_buy("macd_middle", 4, 2) or self.compare_for_buy("macd_middle", 4, 3)) and
                    (self.compare_for_buy("macd_lower", 4, 2) or self.compare_for_buy("macd_lower", 4, 3))):
                data["price"] = 6000
                data["result"] = True
            elif (stage == 5 and self.cryptoService.get_amount("KRW") > 7003 and len(
                    self.cryptoRepository.get_history()) > 5 and
                  (self.compare_for_buy("macd_upper", 5, 2) or self.compare_for_buy("macd_upper", 5, 3)) and
                  (self.compare_for_buy("macd_middle", 4, 2) or self.compare_for_buy("macd_middle", 4, 3)) and
                  (self.compare_for_buy("macd_lower", 4, 2) or self.compare_for_buy("macd_lower", 4, 3))):
                data["price"] = 7000
                data["result"] = True
            elif (stage == 6 and self.cryptoService.get_amount("KRW") > 8003 and len(
                    self.cryptoRepository.get_history()) > 5 and
                  (self.compare_for_buy("macd_upper", 5, 2) or self.compare_for_buy("macd_upper", 5, 3)) and
                  (self.compare_for_buy("macd_middle", 5, 2) or self.compare_for_buy("macd_middle", 5, 3)) and
                  (self.compare_for_buy("macd_lower", 5, 2) or self.compare_for_buy("macd_lower", 5, 3))):
                data["price"] = 8000
                data["result"] = True
            else:
                data["result"] = False
        except Exception as err:
            self.log.error(err)
            data["result"] = False
        return data

    def can_sell(self):
        try:
            if self.tradingRepository.get_my_price() == 0 or self.tradingRepository.get_my_price() is None:
                return False
            profit = (pyupbit.get_current_price(
            f"KRW-{self.TICKER}") - self.tradingRepository.get_my_price()) / self.tradingRepository.get_my_price() * 100
            if (self.cryptoService.get_amount(self.TICKER) != 0 and len(
                    self.cryptoRepository.get_history()) > 5 and profit > 0.8 and
                    (self.compare_for_sell("macd_upper", 4, 2) or self.compare_for_sell("macd_upper", 4, 3)) and
                    (self.compare_for_sell("macd_middle", 4, 2) or self.compare_for_sell("macd_middle", 4, 3)) and
                    (self.compare_for_sell("macd_lower", 3, 2) or self.compare_for_sell("macd_lower", 3, 3))):
                return True
            else:
                return False
        except Exception as err:
            self.log.error(err)
            return False



