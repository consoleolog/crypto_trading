import pyupbit
from pyupbit import Upbit

from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY
from logger import get_logger
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
        self.mailService = mail_service,
        self.cryptoService = crypto_service
        self.log = get_logger(f"{self.TICKER}")

    def get_stage(self, data):
        data['close_slope'] = data['close'].diff()
        data['ema_short_slope'] = data['ema_short'].diff()
        data['ema_middle_slope'] = data['ema_middle'].diff()
        data['ema_long_slope'] = data['ema_long'].diff()

        result = {}

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
            return Exception("STAGE_NOT_FOUND")
        self.cryptoRepository.save_data(data, result["stage"])
        return result

    def BUY(self, inputs):
        if self.cryptoService.get_my_crypto() == 0:
            msg = self.UPBIT.buy_market_order(f"KRW-{self.TICKER}", inputs['price'])
            if msg is None:
                return "ALREADY_BUY"
            if isinstance(msg, dict):
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.TICKER}")
                self.tradingRepository.save_result(msg, "BUY")
                self.mailService.send_file({
                    "content":f"{self.TICKER} 매수 결과 보고",
                    "filename":"buy.csv"
                })
                self.mailService.send_file({
                    "content":f"{self.TICKER} 매수 결과 보고",
                    "filename":"buy_sell.csv"
                })
        else:
            return "ALREADY_BUY"

    def SELL(self, inputs):
        msg = self.UPBIT.sell_market_order(f"KRW-{self.TICKER}", inputs['amount'])
        if isinstance(msg, dict) and 'error' in msg:
            return "ALREADY_SELL"
        if isinstance(msg, dict):
            msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.TICKER}")
            msg['locked'] = 0
            msg['balance'] = 0
            self.tradingRepository.save_result(msg, "SELL")
            self.mailService.send_file({
                "content": f"{self.TICKER} 매수 결과 보고",
                "filename": "buy_sell.csv"
            })

    def init(self):
        self.tradingRepository.create_file()
        self.cryptoRepository.create_file()

    def get_profit(self):
        data = self.tradingRepository.get_trade_history()
        return (pyupbit.get_current_price(f"KRW-{self.TICKER}") - data["market_price"]) /data["market_price"] * 100

    @staticmethod
    def buy_or_sell(data):
        if ((data['macd_10_20_slope'].iloc[-1] >= data['macd_10_20_slope'].iloc[-2] >= data['macd_10_20_slope'].iloc[
            -3]) and
                (data['macd_10_60_slope'].iloc[-1] >= data['macd_10_60_slope'].iloc[-2] >= data['macd_10_20_slope'].iloc[
                    -3]) and
                data['macd_20_60_slope'].iloc[-1] >= data['macd_20_60_slope'].iloc[-2]):
            return "BUY"
