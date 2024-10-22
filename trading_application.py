from pyupbit import Upbit

from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY
from util.common_util import CommonUtil
from util.crypto_util import CryptoUtil
from util.trade_util import TradeUtil


class TradingApplication:

    def __init__(self, ticker):
        self.upbit = Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

        self.crypto_util = CryptoUtil(
            upbit=self.upbit,
            ticker=ticker,
        )

        self.common_util = CommonUtil(ticker=ticker)

        self.trade_util = TradeUtil(
            upbit=self.upbit,
            ticker=ticker,
            crypto_util=self.crypto_util,
            common_util=self.common_util,
        )
