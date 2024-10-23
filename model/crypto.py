from pandas import DataFrame


class Crypto:
    def __init__(self, data: DataFrame):
        self.date = data["date"].iloc[-1]
        self.close = data["close"].iloc[-1]
        self.ema_short = data["ema_short"].iloc[-1]
        self.ema_middle = data["ema_middle"].iloc[-1]
        self.ema_long = data["ema_long"].iloc[-1]
        self.macd_upper = data["macd_upper"].iloc[-1]
        self.macd_middle = data["macd_middle"].iloc[-1]
        self.macd_lower = data["macd_lower"].iloc[-1]