def save_crypto_history(df):
  with open('./data/crypto_history.csv', 'a', encoding='utf-8') as f:
      f.write(f"""\n{df['date'].iloc[-1]}, {df['close'].iloc[-1]}, {df['ema10'].iloc[-1]}, {df['ema20'].iloc[-1]}, {df['ema60'].iloc[-1]}, {df['macd_10_20'].iloc[-1]}, {df['macd_10_60'].iloc[-1]}, {df['macd_20_60'].iloc[-1]} , {df['close_slope'].iloc[-1]}, {df['ema10_slope'].iloc[-1]}, {df['ema20_slope'].iloc[-1]}, {df['ema60_slope'].iloc[-1]} , {df['macd_10_20_slope'].iloc[-1]}, {df['macd_10_60_slope'].iloc[-1]}, {df['macd_20_60_slope'].iloc[-1]}""")
      f.close()


def save_buy_or_sell_history(bs, df):
    from datetime import datetime

    datefmt = '%Y-%m-%d %H:%M:%S'

    dt = datetime.fromisoformat(df['created_at'])

    fdt = dt.strftime(datefmt)

    try:
        df['price']
    except KeyError as ke:
        df['price'] = 0

    with open('./data/crypto_buy_sell_history.csv', 'a', encoding='utf-8') as f:
        f.write(f"\n {fdt}, {df['market']}, {bs}, {df['price']} , {df['market_price']}")
        f.close()
    if bs == "BUY":
        with open('./data/crypto_buy_history.csv', 'a', encoding='utf-8') as f:
            f.write(f"\n {fdt}, {df['market']}, {df['price']} , {df['market_price']}")
            f.close()
    else:
        pass

def get_buy_history():
    import pandas as pd
    data = pd.read_csv('./data/crypto_buy_history.csv', encoding='utf-8')

def get_latest_buy_history():
    import pandas as pd
    try :
        data = pd.read_csv('./data/crypto_buy_history.csv', encoding='utf-8')
        latest_history = data.iloc[-1, 3]
        return latest_history
    except Exception:
        return "None"