import pyupbit
from pyupbit import Upbit
from config import *

from logger import log

from repository import crypto_repository

upbit = Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

def get_balances(ticker):
    """
    :param ticker: 종목 코드
    :return: int
    """

    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def do_buy(ticker, amount, price):
    """
    암호화폐 매수하는 함수
    :param ticker: 종목 코드
    :param amount: 내가 가지고있는 암호화페 양
    :param price:  구매할 가격
    :return: str | dict
    """
    try:
        if amount == 0:
            msg = upbit.buy_market_order(f"KRW-{ticker}", price)
            if msg == None:
                return "ALREADY_BUY"
            if isinstance(msg, dict):
                msg['market_price'] = pyupbit.get_current_price(f"KRW-{ticker}")
                crypto_repository.save_buy_or_sell_history("BUY", msg)
                return msg
            return msg
        else:
            return "ALREADY_BUY"
    except Exception as e:
        raise

def do_sell(ticker, amount):
    """
    암호화폐 매도하는 함수
    :param ticker: 종목 코드
    :param amount: 내가 가지고 있는 암호화폐 양
    :return: str | dict
    """
    try:
        msg = upbit.sell_market_order(f"KRW-{ticker}", amount)
        log.debug(msg)
        # 'error' 키가 있는지 확인
        if isinstance(msg, dict) and 'error' in msg:
            return "ALREADY_SELL"
        if isinstance(msg, dict):
            msg['market_price'] = pyupbit.get_current_price(f"KRW-{ticker}")
            crypto_repository.save_buy_or_sell_history("SELL", msg)
            return msg
        return msg
    except Exception as e:
        raise


def get_sma_data(ticker, interval, count):
    """
    종목 코드, 기간, 양의 따라 데이터 반환
    :param ticker: 종목 코드
    :param interval: 얼마만큼의 기간인지
    :param count: 얼마만큼 가져올건지
    :return: DataFrame
    """

    data = pyupbit.get_ohlcv(ticker=f"KRW-{ticker}", interval=interval, count=count)

    data['sma20'] = data['close'].rolling(20).mean().dropna().astype(int)
    data['sma60'] = data['close'].rolling(60).mean().dropna().astype(int)
    data['sma120'] = data['close'].rolling(120).mean().dropna().astype(int)

    data = data.reset_index()
    data.rename(columns={'index':'date'}, inplace=True)

    data.drop(['open', 'high', 'low', 'volume', 'value'], axis=1, inplace=True)
    data.dropna(inplace=True)

    crypto_repository.save_crypto_history(data)
    return data


def get_gradient(value, rolling):
    return (value.iloc[-2].astype(int) - value.iloc[-1].astype(int)) / rolling

def get_stage(price, short, middle, long, df):
    """
    현재 스테이지 반환하는 함수
    :param df:
    :param price: int
    :param short: int
    :param middle: int
    :param long: int
    :return: str
    """

    log.debug(f"""
    현재가 : {price}
    단기 : {short}
    중기 : {middle}
    장기 : {long}
    MACD (하) : {df['macd_10_20_slope'].iloc[-1]}
    MACD (중) : {df['macd_10_60_slope'].iloc[-1]}
    MACD (상) : {df['macd_20_60_slope'].iloc[-1]}
    """)

    if short >= middle >= long:  # 단 중 장
        return "stage1"
    elif middle >= short >= long:  # 중 단 장
        return "stage2"
    elif middle >= long >= short:  # 중 장 단
        return "stage3"
    elif long >= middle >= short:  # 장  중 단
        return "stage4"
    elif long >= short >= middle:  # 장 단 중
        return "stage5"
    elif short >= long >= middle:  # 단 장 중
        return "stage6"

def calculate_slope(y1, y2, x):
    slope = (y2 - y1) / x
    return slope

def get_crypto_slope(df):
    close_y1 = df['close'].iloc[-1]
    close_y2 = df['close'].iloc[-2]
    cs = calculate_slope(close_y1, close_y2, 1)

    ema10_y1 = df['ema10'].iloc[-1]
    ema10_y2 = df['ema10'].iloc[-2]
    e10s = calculate_slope(ema10_y1, ema10_y2, 20)

    ema20_y1 = df['ema20'].iloc[-1]
    ema20_y2 = df['ema20'].iloc[-2]
    e20s = calculate_slope(ema20_y1, ema20_y2, 60)

    ema60_y1 = df['ema60'].iloc[-1]
    ema60_y2 = df['ema60'].iloc[-2]
    e60s = calculate_slope(ema60_y1, ema60_y2, 120)

    return cs, e10s, e20s, e60s

def calculate_status(df):
    close = df['close'].iloc[-1]

    cs, short, middle, long = get_crypto_slope(df)

    log.debug(f"""
    현재가 : {cs}
    단기 : {short}
    중기 : {middle}
    장기 : {long}""")

    if short >= middle >= long:  # 단 중 장
        log.info(f" stage1 : {close} 안정하게 상승 중.")
        return "stage1"

    elif middle >= short >= long:  # 중 단 장
        log.info(f" stage1 : {close} 안정하게 상승 중.")
        return "stage2"

    elif middle >= long >= short:  # 중 장 단
        log.info(f" stage3 : {close} 하락 추세의 시작. ")
        return "stage3"

    elif long >= middle >= short:  # 장  중 단
        log.info(f" stage4 : {close} 안정하게 하락 중. ")
        return "stage4"

    elif long >= short >= middle:  # 장 단 중
        log.info(f" stage5 : {close} 하락 추세의 끝. ")
        return "stage5"

    elif short >= long >= middle:  # 단 장 중
        log.info(f" stage6 : {close} 상승 추세의 시작. ")
        return "stage6"

def get_ema_data(ticker, interval, count):
    """
    macd의 기울기가 양수일때 감소하면 매도에 점점 가까워지는거고
    macd의 기울기가 음수일때 증가하면 매수에 점점 가까줘지는거임

    매수 신호 : macd의 기울기가 어느정도의 시간동안 음수의 값을 가지다가 양수의 값으로 전환될 때
    매도 신호 : macd의 기울기가 어느정도의 시간동안 양수의 값을 가지다가 음수의 값으로 전환될 때

    :param count:
    :param interval:
    :param ticker: str
    :return: DataFrame
    """
    data = pyupbit.get_ohlcv(ticker=f"KRW-{ticker}", interval=interval, count=count)
    data['ema10'] = data['close'].ewm(span=10, adjust=False, min_periods=10).mean().dropna().astype(int)
    data['ema20'] = data['close'].ewm(span=20, adjust=False, min_periods=20).mean().dropna().astype(int)
    data['ema60'] = data['close'].ewm(span=60, adjust=False, min_periods=60).mean().dropna().astype(int)

    data['macd_10_20'] = data['ema10'] - data['ema20']
    data['macd_10_60'] = data['ema10'] - data['ema60']
    data['macd_20_60'] = data['ema20'] - data['ema60']

    data['macd_10_20_slope'] = data['macd_10_20'].diff()
    data['macd_10_60_slope'] = data['macd_10_60'].diff()
    data['macd_20_60_slope'] = data['macd_20_60'].diff()

    data = data.reset_index()
    data.rename(columns={'index':'date'}, inplace=True)

    data.drop(['open','high','low','volume','value'], axis=1, inplace=True)
    data.dropna(inplace=True)

    crypto_repository.save_crypto_history(data)
    return data

def get_macd_gradient_for_buy(df):
    if df['macd_10_20_slope'].iloc[-1] > 0 and df['macd_10_20_slope'].iloc[-2] > 0 and df['macd_10_20_slope'].iloc[-3] > 0:
        if df['macd_10_60_slope'].iloc[-1] > 0 and df['macd_10_60_slope'].iloc[-2] > 0 and df['macd_10_60_slope'].iloc[-3] > 0:
            if df['macd_20_60_slope'].iloc[-1] > 0 and df['macd_20_60_slope'].iloc[-2] > 0 and df['macd_20_60_slope'].iloc[-3] > 0:
                return "BUY_TRUE"
            else:
                return "BUY_FALSE"
        else:
            return "BUY_FALSE"
    else :
        return "BUY_FALSE"

def get_macd_gradient_for_sell(df):
    if df['macd_10_20_slope'].iloc[-1] < 0 and df['macd_10_20_slope'].iloc[-2] < 0 and df['macd_10_20_slope'].iloc[-3] < 0:
        if df['macd_10_60_slope'].iloc[-1] < 0 and df['macd_10_60_slope'].iloc[-2] < 0 and df['macd_10_60_slope'].iloc[-3] < 0:
            if df['macd_20_60_slope'].iloc[-1] < 0 and df['macd_20_60_slope'].iloc[-2] < 0 and df['macd_20_60_slope'].iloc[-3] < 0:
                return "SELL_TRUE"
            else:
                return "SELL_FALSE"
        else:
            return "SELL_FALSE"
    else :
        return "SELL_FALSE"


