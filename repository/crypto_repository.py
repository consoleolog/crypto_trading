import os


class CryptoRepository:
    def __init__(self, ticker):
        self.data_dir = f'{os.getcwd()}/data'
        self.TICKER = ticker

    def create_file(self):
        if not os.path.exists(f"{self.data_dir}/{self.TICKER}_data.csv"):
            with open(f"{self.data_dir}/{self.TICKER}_data.csv", "w", encoding="utf-8") as f:
                f.write("date")
                f.write(",close")
                f.write(",stage")
                f.write(",ema10")
                f.write(",ema20")
                f.write(",ema60")
                f.write(",macd_short")
                f.write(",macd_middle")
                f.write(",macd_long")
                f.write(",close_slope")
                f.write(",ema10_slope")
                f.write(",ema20_slope")
                f.write(",ema60_slope")
                f.write(",macd_short_slope")
                f.write(",macd_middle_slope")
                f.write(",macd_long_slope")
                f.close()


    def save_data(self, df, stage):
        with open(f'{self.data_dir}/{self.TICKER}_data.csv', 'a', encoding='utf-8') as f:
            f.write(f"\n{df['date'].iloc[-1]}")
            f.write(f",{df['close'].iloc[-1]}")
            f.write(f",{stage}")
            f.write(f",{df['ema10'].iloc[-1]}")
            f.write(f",{df['ema20'].iloc[-1]}")
            f.write(f",{df['ema60'].iloc[-1]}")
            f.write(f",{df['macd_short'].iloc[-1]}")
            f.write(f",{df['macd_middle'].iloc[-1]}")
            f.write(f",{df['macd_long'].iloc[-1]}")
            f.write(f",{df['close_slope'].iloc[-1]}")
            f.write(f",{df['ema10_slope'].iloc[-1]}")
            f.write(f",{df['ema20_slope'].iloc[-1]}")
            f.write(f",{df['ema60_slope'].iloc[-1]}")
            f.write(f",{df['macd_short_slope'].iloc[-1]}")
            f.write(f",{df['macd_middle_slope'].iloc[-1]}")
            f.write(f",{df['macd_long_slope'].iloc[-1]}")