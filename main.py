import time

from langchain_community.document_loaders import DataFrameLoader
from service.crypto_service import *
from service.llm_service import *
from service.mail_service import send_mail

from datetime import datetime, timedelta

# 이전에 실행한 시간을 저장할 변수 초기화
last_send_time = datetime.now()

ticker = "BTC"

def main(df):
    df['date'] = df.apply(lambda row: f"date : {row['date']}", axis=1)

    loader = DataFrameLoader(df, page_content_column="date")

    data = loader.load()

    d_result = decision_buy_or_sell(data)

    if d_result['result'] == "SELL":
        amount = get_balances(ticker)

        if amount == 0:
            pass
        else:
            latest_history = crypto_repository.get_latest_buy_history()
            c_result = compare_with_mine(latest_history, pyupbit.get_current_price(f"KRW-{ticker}"))

            if c_result['result'] == "SELL":
                s_result = do_sell(ticker, amount)
                log.debug(s_result)
                send_mail()
            else:
                pass

    elif d_result['result'] == "BUY":
        amount = get_balances(ticker)
        b_result = do_buy(ticker, amount, 6000)
        log.debug(b_result)
        send_mail()
    else:
        pass

while True:


    try :
        df = get_ema_data(ticker=ticker, interval="minute5",count=240)

        stage = get_stage(df['close'].iloc[-1],df['ema10'].iloc[-1], df['ema20'].iloc[-1], df['ema60'].iloc[-1])

        log.info(stage)

        if stage == "stage6":
            log.info("매수 구간 돌입")
            main(df)

        if stage == "stage1":
            log.info("매도 구간 돌입")
            main(df)

        if stage == "stage4" or stage == "stage5" and get_macd_gradient_for_sell(df) == "BUY_TRUE":
            log.info("매수 신호")
            amount = get_balances(ticker)
            do_sell(ticker, amount)
            send_mail()

        if stage == "stage2" or stage == "stage3" and get_macd_gradient_for_sell(df) == "SELL_TRUE":
            log.info("매도 신호")
            amount = get_balances(ticker)
            do_buy(ticker, amount, 6000)
            send_mail()

        # 1시간마다 send_mail() 호출
        current_time = datetime.now()
        if current_time - last_send_time >= timedelta(hours=1):
            send_mail()
            last_send_time = current_time  # 마지막으로 메일을 보낸 시간을 업데이트


    except Exception as e:
        log.error(e)
        pass

    time.sleep(60)