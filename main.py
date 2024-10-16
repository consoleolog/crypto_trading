import os.path
import time
from multiprocessing.dummy import Pool as ThreadPool

from langchain_community.document_loaders import DataFrameLoader

from app import App

def main(ticker):

    container = App(ticker)
    trading_service = container["tradingService"]
    crypto_service = container["cryptoService"]
    llm_service = container["llmService"]

    if not os.path.exists(f"{os.getcwd()}/data/{ticker}"):
        os.mkdir(f"{os.getcwd()}/data/{ticker}/")

    trading_service.init()

    while True:

        data = crypto_service.EMA("minute60", 180, {
            "short":7,
            "middle":28,
            "long":56,
        })
        get_stage = trading_service.get_stage(data)

        if (get_stage["stage"] == 1 or get_stage["stage"] == 6) and crypto_service.get_my_crypto() != 0:

            data = data.copy()
            data["date"] = data["date"].astype(str)
            loader = DataFrameLoader(data, page_content_column="date")

            df = loader.load()

            trade = llm_service.trading({
                "data":df,
            })

            if trade["result"] == "BUY" and crypto_service.get_my_crypto() == 0:
                trading_service.BUY({
                    "price": 6000,
                })


            if trade["result"] == "SELL" and trading_service.get_profit() > 0.8 :
                trading_service.SELL({
                    "amount": crypto_service.get_my_crypto()
                })

        time.sleep(60)


if __name__ == '__main__':

    tickers = ["BTC","ETH","BCH"]

    pool = ThreadPool(len(tickers))
    result = pool.map(main, tickers)
    pool.close()
    pool.join()