import pyupbit
from pyupbit import Upbit

from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY
from logger import get_logger
from repository.crypto_repository import CryptoRepository
from repository.trading_repository import TradingRepository
from service.mail_service import MailService


class TradingService:
    def __init__(self, ticker:str,
                       crypto_repository: CryptoRepository,
                       trading_repository: TradingRepository,
                       mail_service: MailService):
        self.TICKER = ticker
        self.UPBIT = Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        self.cryptoRepository = crypto_repository
        self.tradingRepository = trading_repository
        self.mailService = mail_service

    def log(self):
        return get_logger(f"{self.TICKER}")

    def EMA(self, interval, count):
        data = pyupbit.get_ohlcv(
            ticker=f"KRW-{self.TICKER}",
            interval=interval,
            count=count
        )

        data["ema10"] = data["close"].ewm(span=10, adjust=False, min_periods=10).mean().dropna().astype(int)
        data["ema20"] = data["close"].ewm(span=20, adjust=False, min_periods=20).mean().dropna().astype(int)
        data["ema60"] = data["close"].ewm(span=60, adjust=False, min_periods=60).mean().dropna().astype(int)

        data["macd_short"] = data["ema10"] - data["ema20"]
        data["macd_middle"] = data["ema10"] - data["ema60"]
        data["macd_long"] = data["ema20"] - data["ema60"]

        data = data.reset_index()
        data.rename(columns={"index": "date"}, inplace=True)

        data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
        data.dropna(inplace=True)

        return data

    def get_stage(self, data):
        data['close_slope'] = data['close'].diff()
        data['ema10_slope'] = data['ema10'].diff()
        data['ema20_slope'] = data['ema20'].diff()
        data['ema60_slope'] = data['ema60'].diff()
        data['macd_short'] = data['ema10'] - data['ema20']
        data['macd_middle'] = data['ema10'] - data['ema60']
        data['macd_long'] = data['ema20'] - data['ema60']
        data['macd_short_slope'] = data['macd_short'].diff()
        data['macd_middle_slope'] = data['macd_middle'].diff()
        data['macd_long_slope'] = data['macd_long'].diff()

        result = {}

        # 단기 > 중기 > 장기
        if data["ema10"].iloc[-1] > data["ema20"].iloc[-1] > data["ema60"].iloc[-1]:
            result["stage"] = 1
        # 중기 > 단기 > 장기
        elif data["ema20"].iloc[-1] > data["ema10"].iloc[-1] > data["EMA60"].iloc[-1]:
            result["stage"] = 2
        # 중기 > 장기 > 단기
        elif data["ema20"].iloc[-1] > data["ema60"].iloc[-1] > data["ema10"].iloc[-1]:
            result["stage"] = 3
        # 장기 > 중기 > 단기
        elif data["ema60"].iloc[-1] > data["ema20"].iloc[-1] > data["ema10"].iloc[-1]:
            result["stage"] = 4
        # 장기 > 단기 > 중기
        elif data["ema60"].iloc[-1] > data["ema10"].iloc[-1] > data["ema20"].iloc[-1]:
            result["stage"] = 5
        # 단기 > 장기 > 중기
        elif data["ema10"].iloc[-1] > data["ema60"].iloc[-1] > data["ema20"].iloc[-1]:
            result["stage"] = 6
        else:
            return Exception("STAGE_NOT_FOUND")
        self.cryptoRepository.save_data(data, result["stage"])
        return result

    def get_my_crypto(self):
        balances = self.UPBIT.get_balances()
        for b in balances:
            if b['currency'] == self.TICKER:
                if b['balance'] is not None:
                    return float(b['balance'])
                else:
                    return 0
        return 0

    def BUY(self, inputs):
        if inputs['amount'] == 0:
            msg = self.UPBIT.buy_market_order(f"KRW-{self.TICKER}", inputs['price'])
            if msg is None:
                return "ALREADY_BUY"
            if isinstance(msg, dict):
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{self.TICKER}")
                self.tradingRepository.save_result(msg, "BUY")
                self.mailService.send_file({
                    "content":f"{self.TICKER} 매수 결과 보고",
                    "filename":f"{self.TICKER}_buy.csv"
                })
                self.mailService.send_file({
                    "content":f"{self.TICKER} 매수 결과 보고",
                    "filename":f"{self.TICKER}_buy_sell.csv"
                })
                return msg

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
                "filename": f"{self.TICKER}_buy_sell.csv"
            })
            return msg

