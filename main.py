import time
from multiprocessing.dummy import Pool as ThreadPool

from app import App
from logger import get_logger


def main(ticker):

    log = get_logger(f"{ticker}")

    container = App(ticker)

    crypto_repository = container["cryptoRepository"]
    trading_repository = container["tradingRepository"]

    crypto_repository.create_file()
    trading_repository.create_file()

    while True:
        trading_service = container["tradingService"]
        crypto_service = container["cryptoService"]
        data = crypto_service.EMA("minute10", 180)
        get_stage = trading_service.get_stage(data)
        time.sleep(5)


if __name__ == '__main__':

    tickers = ["BTC","ETH","BCH"]

    pool = ThreadPool(len(tickers))
    result = pool.map(main,tickers)
    pool.close()
    pool.join()