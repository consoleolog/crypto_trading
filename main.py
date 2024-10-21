import time
from multiprocessing.dummy import Pool as ThreadPool

from langchain_community.document_loaders import DataFrameLoader

from factory import Factory
from logger import get_logger


def main(ticker: str):

    log = get_logger(ticker)

    container = Factory(ticker)
    trading_service = container["tradingService"]
    crypto_service = container["cryptoService"]
    llm_service = container["llmService"]

    trading_service.init()

    counter = 0

    while True:

        data = crypto_service.EMA("minute1", 180, {
            "short":10,
            "middle":20,
            "long":60,
            "signal":1,
        })
        get_stage = trading_service.get_stage(data)

        counter += 1

        if counter == 5:
            log.info("trading starting......")

        if (get_stage["stage"] == 1 or get_stage["stage"] == 6) and crypto_service.get_my_crypto() != 0 and counter > 5:

            data = data.copy()
            data["date"] = data["date"].astype(str)
            loader = DataFrameLoader(data, page_content_column="date")

            df = loader.load()

            buy_or_sell = trading_service.compare()

            if buy_or_sell == "BUY":
                trade = llm_service.trading({
                    "data":df,
                })
                if trade["result"] == "BUY" and crypto_service.get_my_crypto() == 0:
                    log.debug("buying........")
                    trading_service.BUY(6000)
            elif buy_or_sell == "SELL":
                trade = llm_service.trading({
                    "data":df,
                })
                if trade["result"] == "SELL" and trading_service.get_profit() > 0.8 :
                    log.debug("selling......")
                    trading_service.SELL()
        time.sleep(60)


if __name__ == '__main__':

    tickers = ["BTC","ETH","BCH","SOL"]

    pool = ThreadPool(len(tickers))
    result = pool.map(main, tickers)
    pool.close()
    pool.join()