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
            log.info("start trading......")

        data = data.copy()
        data["date"] = data["date"].astype(str)
        loader = DataFrameLoader(data, page_content_column="date")

        df = loader.load()

        # 매수 검토
        if (get_stage["stage"] == 4 or get_stage["stage"] == 5 or get_stage["stage"] == 6) and counter > 5 and crypto_service.get_my_crypto() != 0:
            if trading_service.for_buy(get_stage["stage"]):
                if llm_service.for_buy({"data":df})["result"]:
                    log.debug("buying........")
                    trading_service.BUY(6000)

        # 매도 검토
        if (get_stage["stage"] == 1 or get_stage["stage"] == 2 or get_stage["stage"] == 3) and counter > 5 and crypto_service.get_my_crypto() != 0:
            if trading_service.for_sell(get_stage["stage"]):
                if llm_service.for_sell({"data":df})["result"]:
                    log.debug("selling......")
                    trading_service.SELL()

        time.sleep(60)


if __name__ == '__main__':

    tickers = ["BTC","ETH","BCH","SOL"]

    pool = ThreadPool(len(tickers))
    result = pool.map(main, tickers)
    pool.close()
    pool.join()