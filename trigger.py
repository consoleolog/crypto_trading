from util.crypto_currency_util import CryptoCurrencyUtil


def get_safe_ticker():
    result = []
    ticker_list = CryptoCurrencyUtil.get_ticker_list()
    for a_ticker in ticker_list:
        try:
            score = CryptoCurrencyUtil.coin_validation(a_ticker)
            ema, macd = score["ema"], score["macd"]
            short, e_middle, long = ema["short"], ema["middle"], ema["long"]
            upper, m_middle, lower = macd["upper"], macd["middle"], macd["lower"]
            if all([short > 0.9, e_middle > 0.9, long > 0.9,
                    upper > 0.9, m_middle > 0.9, lower > 0.9]):
                result.append(a_ticker)
        except TypeError:
            pass
    return result

tickers = get_safe_ticker()

