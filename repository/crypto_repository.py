import pandas as pd
import os
from datetime import datetime

class CryptoRepository:
    def __init__(self):
        self.root_dir = f'{os.getcwd()}/data'

    def save_crypto_history(self, df, stage):
        with open(f'{self.root_dir}/crypto_history.csv', 'a', encoding='utf-8') as f:
            f.write(f"""\n{df['date'].iloc[-1]},{df['close'].iloc[-1]},{df['ema10'].iloc[-1]},{df['ema20'].iloc[-1]},{df['ema60'].iloc[-1]},{df['macd_10_20'].iloc[-1]},{df['macd_10_60'].iloc[-1]},{df['macd_20_60'].iloc[-1]},{df['close_slope'].iloc[-1]},{df['ema10_slope'].iloc[-1]},{df['ema20_slope'].iloc[-1]},{df['ema60_slope'].iloc[-1]},{stage},{df['macd_10_20_slope'].iloc[-1]},{df['macd_10_60_slope'].iloc[-1]},{df['macd_20_60_slope'].iloc[-1]}""")
            f.close()

    def save_buy_or_sell_history(self, bs, df):

        datefmt = '%Y-%m-%d %H:%M:%S'

        dt = datetime.fromisoformat(df['created_at'])

        fdt = dt.strftime(datefmt)

        try:
            df['balance']
        except KeyError:
            df['locked'] = 0
            df['balance'] = 0

        with open(f'{self.root_dir}/crypto_buy_sell_history.csv', 'a', encoding='utf-8') as f:
            f.write(f"\n {fdt}, {df['market']}, {bs}, {df['locked']} , {df['market_price']},{df['balance']}")
            f.close()
        if bs == "BUY":
            with open(f'{self.root_dir}/crypto_buy_history.csv', 'a', encoding='utf-8') as f:
                f.write(f"\n {fdt}, {df['market']}, {df['locked']} , {df['market_price']},{df['balance']}")
                f.close()

    def get_crypto_history(self):
        data = pd.read_csv(f'{self.root_dir}/crypto_history.csv', encoding='utf-8')
        return data.tail(n=8)

    def get_buy_history(self):
        data = pd.read_csv(f'{self.root_dir}/crypto_buy_history.csv', encoding='utf-8')
        return data.iloc[-1]