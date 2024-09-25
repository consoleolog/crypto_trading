import os
import time

from config import *

import pandas as pd

from langchain_community.document_loaders import DataFrameLoader
from service.crypto_service import *
from service.llm_service import *
from service.mail_service import send_mail, send_log_file

from datetime import datetime, timedelta

from logger import log

# 이전에 실행한 시간을 저장할 변수 초기화
last_send_time = datetime.now()

ticker = TICKER

log_file = f"{LOG_DIR}/crypto.log"
data_dir = DATA_DIR

def refresh_file():
    for f in os.listdir(data_dir):
        if f.endswith('.csv'):
            fp = os.path.join(data_dir, f)
            ed = pd.DataFrame(columns=pd.read_csv(fp).columns)
            ed.to_csv(fp, index=False)

def main(dataframe):
    dataframe['date'] = dataframe.apply(lambda row: f"date : {row['date']}", axis=1)

    loader = DataFrameLoader(dataframe, page_content_column="date")

    data = loader.load()

    d_result = decision_buy_or_sell(data)
    log.info(d_result['result'])

    if d_result['result'] == "SELL":
        amount = get_balances(ticker)

        if amount == 0:
            log.debug("==============================================")
            log.debug("** 매수 결과 **")
            log.debug("ALREADY_SELL")
            log.debug("==============================================")
            pass
        else:
            latest_history = crypto_repository.get_latest_buy_history()
            if latest_history != "None":
                c_result = compare_with_mine(latest_history, pyupbit.get_current_price(f"KRW-{ticker}"))
                log.info(c_result['result'])

                if c_result['result'] == "PROFIT":
                    s_result = do_sell(ticker, amount)

                    log.debug("==============================================")
                    log.debug("** 매도 결과 **")
                    log.debug(s_result)
                    log.debug("==============================================")

                    if s_result != "ALREADY_SELL":
                        send_mail("매도 결과")

    elif d_result['result'] == "BUY":
        amount = get_balances(ticker)

        if amount != 0:
            b_result = do_buy(ticker, amount, 6000)

            log.debug("==============================================")
            log.debug("** 매수 결과 **")
            log.debug(b_result)
            log.debug("==============================================")

            if b_result != "ALREADY_BUY" and b_result != None and b_result != "None" :
                send_mail("매수 결과")
        else :
            log.debug("==============================================")
            log.debug("** 매수 결과 **")
            log.debug("ALREADY_BUY")
            log.debug("==============================================")
    else:
        pass

# 처음 시작시 파일 초기화
refresh_file()

while True:

    try :
        df = get_ema_data(ticker=ticker, interval="day",count=120)

        stage_result = get_stage(df)
        stage = stage_result['stage']

        log.info(f"""
        ==================
        #                #
        #     {stage}     #
        #                #
        ==================
        """)

        result = decision_using_stage(stage, df)

        if result['result'] == "BUY_TRUE":
            log.info(f"""
            ==================
            #                #
            #   매수 신호    #
            #                #
            ==================
            """)
            main(stage_result['data'])

        elif result['result'] == "SELL_TRUE":
            log.info(f"""
            ==================
            #                #
            #   매도 신호    #
            #                #
            ==================
            """)
            main(stage_result['data'])
        else :
            pass


        current_time = datetime.now()

        # 3 시간마다 로그 파일 , 데이터 파일 초기화
        if current_time - last_send_time >= timedelta(hours=3):
            log.debug("로그 파일 초기화")
            send_log_file("로그 파일 초기화 전 백업")
            send_mail("데이터 파일 초기화 전 백업")

            refresh_file()

            # 마지막으로 메일을 보낸 시간을 업데이트
            last_send_time = current_time

    except Exception as e:
        log.error("=========================================")
        log.error(e)
        log.error("=========================================")
        pass

    time.sleep(120)