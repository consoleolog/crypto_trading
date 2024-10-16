import pyupbit
from pyupbit import Upbit

from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY


class CryptoService:
    def __init__(self, ticker):
        self.UPBIT = Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        self.TICKER = ticker

    def get_my_crypto(self):
        balances = self.UPBIT.get_balances()
        for b in balances:
            if b['currency'] == self.TICKER:
                if b['balance'] is not None:
                    return float(b['balance'])
                else:
                    return 0
        return 0

    def EMA(self, interval, count, ema_options):
        data = pyupbit.get_ohlcv(
            ticker=f"KRW-{self.TICKER}",
            interval=interval,
            count=count
        )

        data["ema_short"] = data["close"].ewm(span=ema_options["short"], adjust=False, min_periods=ema_options["short"]).mean().dropna().astype(int)
        data["ema_middle"] = data["close"].ewm(span=ema_options["middle"], adjust=False, min_periods=ema_options["middle"]).mean().dropna().astype(int)
        data["ema_long"] = data["close"].ewm(span=ema_options["long"], adjust=False, min_periods=ema_options["long"]).mean().dropna().astype(int)

        data["macd_short"] = data["ema_short"] - data["ema_middle"]
        data["macd_middle"] = data["ema_short"] - data["ema_long"]
        data["macd_long"] = data["ema_middle"] - data["ema_long"]

        data['macd_short_slope'] = data['macd_short'].diff()
        data['macd_middle_slope'] = data['macd_middle'].diff()
        data['macd_long_slope'] = data['macd_long'].diff()

        data = data.reset_index()
        data.rename(columns={"index": "date"}, inplace=True)

        data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
        data.dropna(inplace=True)

        return data