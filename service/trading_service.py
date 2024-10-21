import os.path

import pyupbit
from pandas import DataFrame
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

    def get_stage(self, data: DataFrame)-> dict[str, int]:
        data['close_slope'] = data['close'].diff()
        data['ema_short_slope'] = data['ema_short'].diff()
        data['ema_middle_slope'] = data['ema_middle'].diff()
        data['ema_long_slope'] = data['ema_long'].diff()
        data['signal_slope'] = data['signal'].diff()
        data['histogram_upper'] = data['macd_upper'] - data['signal']
        data['histogram_middle'] = data['macd_middle'] - data['signal']
        data['histogram_lower'] = data['macd_lower'] - data['signal']

        result = {
            "stage": 0
        }

        # 단기 > 중기 > 장기
        if data["ema_short"].iloc[-1] > data["ema_middle"].iloc[-1] > data["ema_long"].iloc[-1]:
            result["stage"] = 1
        # 중기 > 단기 > 장기
        elif data["ema_middle"].iloc[-1] > data["ema_short"].iloc[-1] > data["ema_long"].iloc[-1]:
            result["stage"] = 2
        # 중기 > 장기 > 단기
        elif data["ema_middle"].iloc[-1] > data["ema_long"].iloc[-1] > data["ema_short"].iloc[-1]:
            result["stage"] = 3
        # 장기 > 중기 > 단기
        elif data["ema_long"].iloc[-1] > data["ema_middle"].iloc[-1] > data["ema_short"].iloc[-1]:
            result["stage"] = 4
        # 장기 > 단기 > 중기
        elif data["ema_long"].iloc[-1] > data["ema_short"].iloc[-1] > data["ema_middle"].iloc[-1]:
            result["stage"] = 5
        # 단기 > 장기 > 중기
        elif data["ema_short"].iloc[-1] > data["ema_long"].iloc[-1] > data["ema_middle"].iloc[-1]:
            result["stage"] = 6
        else:
            raise Exception("NOT_FOUND_STAGE")

        self.cryptoRepository.save(Crypto(data), result["stage"])
        return result

    def BUY(self, price: int) -> type(None):
        if self.cryptoService.get_my_crypto() == 0:
            msg = self.UPBIT.buy_market_order(f"KRW-{self.TICKER}", price)
            if isinstance(msg, dict):
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.TICKER}")

                self.tradingRepository.save(Trade(msg), "BUY")
                self.mailService.send_file({
                    "content":f"{self.TICKER} 매수 결과 보고",
                    "filename":"buy.csv"
                })
                self.mailService.send_file({
                    "content":f"{self.TICKER} 매수 결과 보고",
                    "filename":"buy_sell.csv"
                })

    def SELL(self) -> type(None):
        msg = self.UPBIT.sell_market_order(f"KRW-{self.TICKER}", self.cryptoService.get_my_crypto())
        if isinstance(msg, dict):
            msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.TICKER}")
            msg['locked'] = 0
            self.tradingRepository.save(Trade(msg), "SELL")
            self.mailService.send_file({
                "content": f"{self.TICKER} 매도 결과 보고",
                "filename": "buy_sell.csv"
            })

    def init(self) -> type(None):
        if not os.path.exists(f"{os.getcwd()}/data"):
            os.mkdir(f"{os.getcwd()}/data")

        if not os.path.exists(f"{os.getcwd()}/data/{self.TICKER}"):
            os.mkdir(f"{os.getcwd()}/data/{self.TICKER}")

        self.tradingRepository.create_file()
        self.cryptoRepository.create_file()

    def get_profit(self) -> float:
        data = self.tradingRepository.get_trade_history()
        return (pyupbit.get_current_price(f"KRW-{self.TICKER}") - data["market_price"]) /data["market_price"] * 100

    def compare(self):

        result = {}

        data = self.cryptoRepository.get_history()
        if ((data["macd_upper"].iloc[-1] > data["macd_upper"].iloc[-3]) and
            (data["macd_upper"].iloc[-2] > data["macd_upper"].iloc[-4]) and
            (data["macd_upper"].iloc[-3] > data["macd_upper"].iloc[-5])):
            result["upper"] = "BUY"

        if ((data["macd_middle"].iloc[-1] > data["macd_middle"].iloc[-3]) and
            (data["macd_middle"].iloc[-2] > data["macd_middle"].iloc[-4]) and
            (data["macd_middle"].iloc[-3] > data["macd_middle"].iloc[-5])):
            result["middle"] = "BUY"

        if ((data["macd_lower"].iloc[-1] > data["macd_lower"].iloc[-3]) and
            (data["macd_lower"].iloc[-2] > data["macd_lower"].iloc[-4]) and
            (data["macd_lower"].iloc[-3] > data["macd_lower"].iloc[-5])):
            result["lower"] = "BUY"

        if ((data["macd_upper"].iloc[-1] < data["macd_upper"].iloc[-3]) and
                (data["macd_upper"].iloc[-2] < data["macd_upper"].iloc[-4]) and
                (data["macd_upper"].iloc[-3] < data["macd_upper"].iloc[-5])):
            result["upper"] = "SELL"

        if ((data["macd_middle"].iloc[-1] < data["macd_middle"].iloc[-3]) and
                (data["macd_middle"].iloc[-2] < data["macd_middle"].iloc[-4]) and
                (data["macd_middle"].iloc[-3] < data["macd_middle"].iloc[-5])):
            result["middle"] = "SELL"

        if ((data["macd_lower"].iloc[-1] < data["macd_lower"].iloc[-3]) and
                (data["macd_lower"].iloc[-2] < data["macd_lower"].iloc[-4]) and
                (data["macd_lower"].iloc[-3] < data["macd_lower"].iloc[-5])):
            result["lower"] = "SELL"

        if result["upper"] == "BUY" and result["middle"] == "BUY" and result ["lower"] == "BUY":
            return "BUY"
        elif result["upper"] == "SELL" and result["middle"] == "SELL" and result ["lower"] == "SELL":
            return "SELL"
        else :
            return "None"

    def can_buy(self, stage):
        if stage == 1:
            pass


