from pandas import DataFrame


class Crypto:
    def __init__(self, data: DataFrame):
        self.date = data["date"].iloc[-1]
        self.close = data["close"].iloc[-1]
        self.ema_short = data["ema_short"].iloc[-1]
        self.ema_middle = data["ema_middle"].iloc[-1]
        self.ema_long = data["ema_long"].iloc[-1]
        self.signal = data["signal"].iloc[-1]
        self.histogram_upper = data["histogram_upper"].iloc[-1]
        self.histogram_middle = data["histogram_middle"].iloc[-1]
        self.histogram_lower = data["histogram_lower"].iloc[-1]
        self.macd_upper = data["macd_upper"].iloc[-1]
        self.macd_middle = data["macd_middle"].iloc[-1]
        self.macd_lower = data["macd_lower"].iloc[-1]
        self.close_slope = data["close_slope"].iloc[-1]
        self.ema_short_slope = data["ema_short_slope"].iloc[-1]
        self.ema_middle_slope = data["ema_middle_slope"].iloc[-1]
        self.ema_long_slope = data["ema_long_slope"].iloc[-1]
        self.signal_slope = data["signal_slope"].iloc[-1]
        self.macd_upper_slope = data["macd_upper_slope"].iloc[-1]
        self.macd_middle_slope = data["macd_middle_slope"].iloc[-1]
        self.macd_lower_slope = data["macd_lower_slope"].iloc[-1]