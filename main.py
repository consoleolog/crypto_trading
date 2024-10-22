import time
from multiprocessing.dummy import Pool as ThreadPool


from factory import Factory
from service.crypto_service import CryptoService
from service.trading_service import TradingService


def main(ticker: str):

    container = Factory(ticker)
    trading_service: TradingService = container["tradingService"]
    crypto_service: CryptoService = container["cryptoService"]

    trading_service.init()

    while True:

        data = crypto_service.EMA("minute1", 120, {
            "short":10,
            "middle":20,
            "long":40,
            "signal":1,
        })

        stage: int = trading_service.get_stage(data)

        # 매수 검토
        if (stage == 4 or stage == 5 or stage == 6) and  trading_service.for_buy(stage) == True and trading_service.data_check() == True:
            if crypto_service.get_amount("KRW") > 6003:
                trading_service.BUY(6000)

        # 매도 검토
        if (stage == 1 or stage == 2 or stage == 3) and crypto_service.get_my_crypto() != 0 and trading_service.data_check() == True:
            if trading_service.for_sell(stage) and trading_service.get_profit() > 0.8:
                trading_service.SELL()

        time.sleep(60)


if __name__ == '__main__':

    tickers: list[str] = ["BTC","ETH","BCH","SOL"]
    # tickers: list[str] = ["XRP","DOGE","SHIB"]

    pool = ThreadPool(len(tickers))
    result = pool.map(main, tickers)
    pool.close()
    pool.join()