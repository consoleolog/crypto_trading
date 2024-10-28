import os


class CryptoCurrencyUtil:

    @staticmethod
    def get_ema(data, opt):
        data["ema_short"] = data["close"].ewm(span=opt["short"]).mean()
        data["ema_middle"] = data["close"].ewm(span=opt["middle"]).mean()
        data["ema_long"] = data["close"].ewm(span=opt["long"]).mean()
        return data

    @staticmethod
    def get_macd(data):
        data["macd_upper"] = data["ema_short"] - data["ema_middle"]  # (상)
        data["macd_middle"] = data["ema_short"] - data["ema_long"]  # (중)
        data["macd_lower"] = data["ema_middle"] - data["ema_long"]  # (하)
        data["upper_result"] = data["macd_upper"] > data["macd_upper"].shift(1)
        data["middle_result"] = data["macd_middle"] > data["macd_middle"].shift(1)
        data["lower_result"] = data["macd_lower"] > data["macd_lower"].shift(1)
        return data

    @staticmethod
    def get_stage(data):
        short, middle, long = data["ema_short"], data["ema_middle"], data["ema_long"]
        if short >= middle >= long:
            return 1
            # 중기 > 단기 > 장기
        elif middle >= short >= long:
            return 2
            # 중기 > 장기 > 단기
        elif middle >= long >= short:
            return 3
            # 장기 > 중기 > 단기
        elif long >= middle >= short:
            return 4
            # 장기 > 단기 > 중기
        elif long >= short >= middle:
            return 5
            # 단기 > 장기 > 중기
        elif short >= long >= middle:
            return 6



    @staticmethod
    def create_data_dir():
        if not os.path.exists(f"{os.getcwd()}/data"):
            os.mkdir(f"{os.getcwd()}/data")