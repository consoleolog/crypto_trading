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
                msg['balance'] = get_balances(ticker)
                crypto_repository.save_buy_or_sell_history("BUY", msg)
                return msg
            return msg
        else:
            return "ALREADY_BUY"
    except Exception as e:
        log.error(e)
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
        # 'error' 키가 있는지 확인
        if isinstance(msg, dict) and 'error' in msg:
            return "ALREADY_SELL"
        if isinstance(msg, dict):
            msg['market_price'] = pyupbit.get_current_price(f"KRW-{ticker}")
            crypto_repository.save_buy_or_sell_history("SELL", msg)
            return msg
        return msg
    except Exception as e:
        log.error(e)
        raise

def get_stage(df):
    """
    현재 스테이지 반환하는 함수
    """
    df['close_slope'] = df['close'].diff()

    df['ema10_slope'] = df['ema10'].diff()
    df['ema20_slope'] = df['ema20'].diff()
    df['ema60_slope'] = df['ema60'].diff()

    df['macd_10_20'] = df['ema10'] - df['ema20']
    df['macd_10_60'] = df['ema10'] - df['ema60']
    df['macd_20_60'] = df['ema20'] - df['ema60']

    df['macd_10_20_slope'] = df['macd_10_20'].diff()
    df['macd_10_60_slope'] = df['macd_10_60'].diff()
    df['macd_20_60_slope'] = df['macd_20_60'].diff()

    short = df['ema10'].iloc[-1]
    middle = df['ema20'].iloc[-1]
    long = df['ema60'].iloc[-1]

    log.debug(f"""
    ================================================= 
    ## ** 단순 가격 **                                               
    ## 현재가 : {df['close'].iloc[-1]}                         
    ## 단기   : {short}                                         
    ## 중기   : {middle}                                    
    ## 장기   : {long}                                              
    ## MACD (하) : {df['macd_10_20'].iloc[-1]}                
    ## MACD (중) : {df['macd_10_60'].iloc[-1]}        
    ## MACD (상) : {df['macd_20_60'].iloc[-1]}           
    ================================================= 
    ## ** 기울기 **                                            
    ## 현재가 : {df['close_slope'].iloc[-1]}               
    ## 단기   : {df['ema10_slope'].iloc[-1]}                
    ## 중기   : {df['ema20_slope'].iloc[-1]}                
    ## 장기   : {df['ema60_slope'].iloc[-1]}                
    ## MACD (하) : {df['macd_10_20_slope'].iloc[-1]}      
    ## MACD (중) : {df['macd_10_60_slope'].iloc[-1]}     
    ## MACD (상) : {df['macd_20_60_slope'].iloc[-1]}    
    =================================================    
    """)

    if short >= middle >= long:  # 단 중 장
        return {
            "stage": "stage1",
            "data" : df
        }
    elif middle >= short >= long:  # 중 단 장
        return {
            "stage": "stage2",
            "data": df
        }
    elif middle >= long >= short:  # 중 장 단
        return {
            "stage": "stage3",
            "data": df
        }
    elif long >= middle >= short:  # 장  중 단
        return {
            "stage": "stage4",
            "data": df
        }
    elif long >= short >= middle:  # 장 단 중
        return {
            "stage": "stage5",
            "data": df
        }
    elif short >= long >= middle:  # 단 장 중
        return {
            "stage": "stage6",
            "data": df
        }



def get_ema_data(ticker, interval, count):
    """
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

    data = data.reset_index()
    data.rename(columns={'index':'date'}, inplace=True)

    data.drop(['open','high','low','volume','value'], axis=1, inplace=True)
    data.dropna(inplace=True)

    return data

def analyze_slope(df):
    log.info("=================================================")
    log.info("## ** 기울기 분석 **")
    if df['macd_10_20_slope'].iloc[-1] < df['macd_10_20_slope'].iloc[-2]:
        log.info("[1] MACD (하) 기울기 감소")
        if df['macd_10_20_slope'].iloc[-2] < df['macd_10_20_slope'].iloc[-3]:
            log.info("[2] MACD (하) 기울기 감소")
            if df['macd_10_20_slope'].iloc[-3] < df['macd_10_20_slope'].iloc[-4]:
                log.info("[3] MACD (하) 기울기 감소")
            else:
                log.info("[3] MACD (하) 기울기 증가")
        else:
            log.info("[2] MACD (하) 기울기 증가")
    else:
        log.info("[1] MACD (하) 기울기 증가")



    if df['macd_10_60_slope'].iloc[-1] < df['macd_10_60_slope'].iloc[-2]:
        log.info("[1] MACD (중) 기울기 감소")
        if df['macd_10_60_slope'].iloc[-2] < df['macd_10_60_slope'].iloc[-3]:
            log.info("[2] MACD (중) 기울기 감소")
            if df['macd_10_60_slope'].iloc[-3] < df['macd_10_60_slope'].iloc[-4]:
                log.info("[3] MACD (중) 기울기 감소")
            else:
                log.info("[3] MACD (중) 기울기 증가")
        else:
            log.info("[2] MACD (중) 기울기 증가")
    else:
        log.info("[1] MACD (중) 기울기 증가")


    if df['macd_20_60_slope'].iloc[-1] < df['macd_20_60_slope'].iloc[-2]:
        log.info("[1] MACD (상) 기울기 감소")
        if df['macd_20_60_slope'].iloc[-2] < df['macd_20_60_slope'].iloc[-3]:
            log.info("[2] MACD (상) 기울기 감소")
            if df['macd_20_60_slope'].iloc[-3] < df['macd_20_60_slope'].iloc[-4]:
                log.info("[3] MACD (상) 기울기 감소")
            else:
                log.info("[3] MACD (상) 기울기 증가")
        else:
            log.info("[2] MACD (상) 기울기 증가")
    else:
        log.info("[1] MACD (상) 기울기 증가")


def decision_using_stage(stage):
    df = crypto_repository.get_crypto_history()

    ## STAGE 1 ##
    if stage == "stage1":
        if ((df['macd_10_20_slope'].iloc[-1] <= df['macd_10_20_slope'].iloc[-2] <= df['macd_10_20_slope'].iloc[-3]) and
            (df['macd_10_60_slope'].iloc[-1] <= df['macd_10_60_slope'].iloc[-2] <= df['macd_10_60_slope'].iloc[-3]) and
             df['macd_20_60_slope'].iloc[-1] <= df['macd_20_60_slope'].iloc[-2] <= df['macd_10_60_slope'].iloc[-3]):
            return {
                "stage": "stage1",
                "result": "SELL_TRUE"
            }
        else:
            return {
                "stage": "stage1",
                "result": "SELL_FALSE"
            }
    ## STAGE 2 ##
    elif stage == "stage2":
        if ((df['macd_10_20_slope'].iloc[-1] <= df['macd_10_20_slope'].iloc[-2] <= df['macd_10_20_slope'].iloc[-3]) and
            (df['macd_10_60_slope'].iloc[-1] <= df['macd_10_60_slope'].iloc[-2]) and
             df['macd_20_60_slope'].iloc[-1] <= df['macd_20_60_slope'].iloc[-2]):
            return {
                "stage": "stage2",
                "result": "SELL_TRUE"
            }
        else:
            return {
                "stage": "stage2",
                "result": "SELL_FALSE"
            }
    ## STAGE 3 ##
    elif stage == "stage3":
        if ((df['macd_10_20_slope'].iloc[-1] <= df['macd_10_20_slope'].iloc[-2]) and
            (df['macd_10_60_slope'].iloc[-1] <= df['macd_10_60_slope'].iloc[-2]) and
             df['macd_20_60_slope'].iloc[-1] <= df['macd_20_60_slope'].iloc[-2]):
            return {
                "stage": "stage3",
                "result": "SELL_TRUE"
            }
        else:
            return {
                "stage": "stage3",
                "result": "SELL_FALSE"
            }
    ## STAGE 4 ##
    elif stage == "stage4":
        if ((df['macd_10_20_slope'].iloc[-1] >= df['macd_10_20_slope'].iloc[-2] >= df['macd_10_20_slope'].iloc[-3] >= df['macd_10_20_slope'].iloc[-4]) and
            (df['macd_10_60_slope'].iloc[-1] >= df['macd_10_60_slope'].iloc[-2] >= df['macd_10_20_slope'].iloc[-3] >= df['macd_10_20_slope'].iloc[-4]) and
             df['macd_20_60_slope'].iloc[-1] >= df['macd_20_60_slope'].iloc[-2]):
            return {
                "stage": "stage4",
                "result": "BUY_TRUE"
            }
        else:
            return {
                "stage": "stage4",
                "result": "BUY_FALSE"
            }
    ## STAGE 5 ##
    elif stage == "stage5":
        if ((df['macd_10_20_slope'].iloc[-1] >= df['macd_10_20_slope'].iloc[-2] >= df['macd_10_20_slope'].iloc[-3] >= df['macd_10_20_slope'].iloc[-4]) and
            (df['macd_10_60_slope'].iloc[-1] >= df['macd_10_60_slope'].iloc[-2] >= df['macd_10_20_slope'].iloc[-3]) and
             df['macd_20_60_slope'].iloc[-1] >= df['macd_20_60_slope'].iloc[-2]):
            return {
                "stage": "stage5",
                "result": "BUY_TRUE"
            }
        else:
            return {
                "stage": "stage5",
                "result": "BUY_FALSE"
            }
    ## STAGE 6 ##
    elif stage == "stage6":
        if ((df['macd_10_20_slope'].iloc[-1] >= df['macd_10_20_slope'].iloc[-2] >= df['macd_10_20_slope'].iloc[-3]) and
            (df['macd_10_60_slope'].iloc[-1] >= df['macd_10_60_slope'].iloc[-2] >= df['macd_10_20_slope'].iloc[-3]) and
             df['macd_20_60_slope'].iloc[-1] >= df['macd_20_60_slope'].iloc[-2] ):
            return {
                "stage": "stage6",
                "result": "BUY_TRUE"
            }
        else:
            return {
                "stage": "stage6",
                "result": "BUY_FALSE"
            }
    else:
        return {
            "result": "None"
        }




