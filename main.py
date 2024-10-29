import time

from crypto_currency_app import CryptoCurrencyApplication
from util.crypto_currency_util import CryptoCurrencyUtil

from multiprocessing.dummy import Pool as ThreadPool

def print_starting_banner(app, ticker):
    app.log.info(f"{ticker} trading start....")

def main(ticker):
    crypto_currency_app = CryptoCurrencyApplication(ticker)

    crypto_currency_service = crypto_currency_app.crypto_currency_service

    CryptoCurrencyUtil.create_data_dir()

    crypto_currency_service.create_crypto_currency_data_files()

    print_starting_banner(crypto_currency_app, ticker)

    while True:
        crypto_currency_service.start_trading({
            "short": 10,
            "middle": 20,
            "long": 60,
        })
        time.sleep(60)


if __name__ == '__main__':
    tickers: list[str] = ["BSV"]

    pool = ThreadPool(len(tickers))
    pool.map(main, tickers)
    pool.close()
    pool.join()