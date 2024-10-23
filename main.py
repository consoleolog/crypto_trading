import os
import time
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
from sklearn.linear_model import LinearRegression

from config import get_logger
from trading_application import TradingApplication

def main(ticker: str):
    if not os.path.exists(f"{os.getcwd()}/data"):
        os.mkdir(f"{os.getcwd()}/data")

    log = get_logger(ticker)

    app = TradingApplication(ticker)

    app.common_util.init()

    refer_data = app.crypto_util.create_reference_data()

    model = LinearRegression().fit(np.array(refer_data["macd_middle"]).reshape((-1,1)), np.array(refer_data["macd_lower"]))


    log.info(f"start {ticker} trading....")

    while True:
        try:
            app.trade_util.response_stage(
                app.trade_util.get_stage(
                    app.crypto_util.ema("minute1", 120, {
                        "short": 10,
                        "middle": 20,
                        "long": 40,
                        "signal": 9,
                    }), model ), model)
            time.sleep(60)
        except Exception as err:
            raise Exception(err)

if __name__ == '__main__':

    tickers: list[str] = ["ETH"]


    pool = ThreadPool(len(tickers))
    result = pool.map(main, tickers)
    pool.close()
    pool.join()