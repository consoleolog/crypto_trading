import time
from typing import Final

from crypto_currency_app import CryptoCurrencyApplication
from util.crypto_currency_util import CryptoCurrencyUtil

from multiprocessing.dummy import Pool as ThreadPool

def print_starting_banner(app, ticker, price):
    app.log.info(f"{ticker} trading start....")
    app.log.warning(f"{ticker}'s global order price is {price}....")

tickers:list[str] = CryptoCurrencyUtil.setting_ticker()

def main(ticker):
    crypto_currency_app = CryptoCurrencyApplication(ticker)

    crypto_currency_service = crypto_currency_app.crypto_currency_service

    CryptoCurrencyUtil.create_data_dir()

    crypto_currency_service.create_crypto_currency_data_files()

    price: Final = ( crypto_currency_service.get_krw() / len(tickers) )

    print_starting_banner(crypto_currency_app, ticker, price)

    while True:
        crypto_currency_service.start_trading(
            ema_options = {
                "short": 10,
                "middle": 20,
                "long": 60,
            }, price=price, interval="minutes1")
        time.sleep(60)

if __name__ == '__main__':

    pool = ThreadPool(len(tickers))
    pool.map(main, tickers)
    pool.close()
    pool.join()