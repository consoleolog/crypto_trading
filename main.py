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

        stage: int = trading_service.get_stage(crypto_service.EMA("minute1", 120, {
            "short":10,
            "middle":20,
            "long":40,
            "signal":1,
        }))

        # 매수 검토
        if stage == 4 or stage == 5 or stage == 6:
            msg = trading_service.can_buy(stage)
            if msg["result"]:
                trading_service.BUY(msg["price"])

        # 매도 검토
        if (stage == 1 or stage == 2 or stage == 3) and trading_service.can_sell() == True:
            trading_service.SELL()

        time.sleep(60)


if __name__ == '__main__':

    tickers: list[str] = ["BTC","ETH","BCH","SOL"]
    # tickers: list[str] = ["XRP","DOGE","SHIB"]

    pool = ThreadPool(len(tickers))
    result = pool.map(main, tickers)
    pool.close()
    pool.join()