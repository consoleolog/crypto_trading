import os
import time

import pandas as pd

from langchain_community.document_loaders import DataFrameLoader
from service.crypto_service import *
from service.llm_service import *
from service.mail_service import send_mail, send_log_file

from datetime import datetime, timedelta

# 이전에 실행한 시간을 저장할 변수 초기화
last_send_time = datetime.now()

ticker = "BTC"

def main(dataframe):
    dataframe['date'] = dataframe.apply(lambda row: f"date : {row['date']}", axis=1)

    loader = DataFrameLoader(dataframe, page_content_column="date")

    data = loader.load()

    d_result = decision_buy_or_sell(data)
    log.info(d_result['result'])

    if d_result['result'] == "SELL":
        amount = get_balances(ticker)

        if amount == 0:
            pass
        else:
            latest_history = crypto_repository.get_latest_buy_history()
            c_result = compare_with_mine(latest_history, pyupbit.get_current_price(f"KRW-{ticker}"))
            log.info(c_result['result'])

            if c_result['result'] == "SELL":
                s_result = do_sell(ticker, amount)
                log.debug(s_result)
                if s_result != "ALREADY_SELL":
                    send_mail("매도 결과")
            else:
                pass

    elif d_result['result'] == "BUY":
        amount = get_balances(ticker)
        b_result = do_buy(ticker, amount, 6000)
        log.debug(b_result)
        if b_result != "ALREADY_BUY" and b_result != None and b_result != "None" :
            send_mail("매수 결과")
    else:
        pass

while True:

    try :
        df = get_ema_data(ticker=ticker, interval="minute5",count=240)

        stage = get_stage(df['close'].iloc[-1],df['ema10'].iloc[-1], df['ema20'].iloc[-1], df['ema60'].iloc[-1], df)

        log.info(stage)

        if stage == "stage4" or stage == "stage5" or stage == "stage6":
            macd_b_result = get_macd_gradient_for_buy(df)
            log.info(macd_b_result)
            if macd_b_result == "BUY_TRUE":
                log.info("매수 신호")
                main(df)

        if (stage == "stage1" or stage == "stage2" or stage == "stage3") and get_macd_gradient_for_sell(df) == "SELL_TRUE":
            macd_s_result = get_macd_gradient_for_sell(df)
            log.info(macd_s_result)
            if macd_s_result == "SELL_TRUE":
                log.info("매도 신호")
                main(df)

        current_time = datetime.now()

        # 12시간마다 로그 파일 , 데이터 파일 초기화
        if current_time - last_send_time >= timedelta(hours=3):
            log.debug("로그 파일 초기화")
            send_log_file("로그 파일 초기화 전 백업")
            log_dir = "./logs"
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            send_mail("데이터 파일 초기화 전 백업")
            data_dir = "./data"
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    file_path = os.path.join(data_dir, filename)

                    empty_df = pd.DataFrame(columns=pd.read_csv(file_path).columns)

                    empty_df.to_csv(file_path, index=False)
            # 마지막으로 메일을 보낸 시간을 업데이트
            last_send_time = current_time

    except Exception as e:
        log.error(e)
        pass

    time.sleep(100)