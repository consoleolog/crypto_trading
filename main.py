import os
import time
from multiprocessing.dummy import Pool as ThreadPool

from trading_application import TradingApplication

def main(ticker: str):
    app = TradingApplication(ticker)

    if not os.path.exists(f"{os.getcwd()}/data"):
        os.mkdir(f"{os.getcwd()}/data")

    app.common_util.init()

    while True:
        try:
            app.trade_util.response_stage(
                app.trade_util.get_stage(
                    app.crypto_util.ema("minute1", 120, {
                        "short": 10,
                        "middle": 20,
                        "long": 40,
                        "signal": 9,
                    })
            ))
            time.sleep(60)
        except Exception as err:
            raise Exception(err)

if __name__ == '__main__':

    tickers: list[str] = ["XRP","DOGE","BSV","ETH","SOL","AAVE","UNI"]
    # tickers: list[str] = ["XRP","DOGE","SHIB","BSV","ETH","BTC","BCH"]

    pool = ThreadPool(len(tickers))
    result = pool.map(main, tickers)
    pool.close()
    pool.join()