import os
import time
import threading
from multiprocessing.dummy import Pool as ThreadPool

from config import get_logger
from trading_application import TradingApplication


def get_models(app, ticker):
    log = get_logger(ticker)

    result = app.crypto_util.create_model()
    scores, models = result["scores"], result["models"]

    log.info(f"""
                ##### {ticker} #####
            ema 단기 : {scores["ema_short"]}
            ema 중기 : {scores["ema_middle"]}
            ema 장기 : {scores["ema_long"]}

            macd 상 : {scores["macd_upper"]}
            macd 중 : {scores["macd_middle"]}
            macd 하 : {scores["macd_lower"]}
            """)

    return models

def update_models(app, ticker, models):
    while True:
        time.sleep(7200)
        new_models = get_models(app, ticker)
        models.clear()
        models.update(new_models)


def main(ticker: str):
    if not os.path.exists(f"{os.getcwd()}/data"):
        os.mkdir(f"{os.getcwd()}/data/")

    log = get_logger(ticker)

    app = TradingApplication(ticker)

    app.common_util.init()

    log.info(f"start {ticker} trading....")

    models = get_models(app, ticker)

    model_update_thread = threading.Thread(target=update_models, args=(app, ticker, models), daemon=True)
    model_update_thread.start()

    while True:
        try:
            app.trade_util.response_stage(
                app.trade_util.get_stage(
                    app.crypto_util.ema("minute1", 120, {
                        "short": 10,
                        "middle": 20,
                        "long": 40,
                        "signal": 9,
                    }), models
                ), models
            )
            time.sleep(60)
        except Exception as err:
            log.error(err)


if __name__ == '__main__':
    tickers: list[str] = ["ETH","BTC","AAVE","SOL"]
    # "BCH" "BSV" "AVAX" "ETC" "BTG"

    pool = ThreadPool(len(tickers))
    pool.map(main, tickers)
    pool.close()
    pool.join()
