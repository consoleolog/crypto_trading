import time

from config import *


from langchain_community.document_loaders import DataFrameLoader

from service.mail_service import send_mail, send_log_file

from service import ai_service, crypto_service

from datetime import datetime, timedelta

from logger import log

# 이전에 실행한 시간을 저장할 변수 초기화
last_send_time = datetime.now()

ticker = TICKER


def main(dataframe):
    dataframe = dataframe.copy()
    dataframe['date'] = dataframe['date'].astype(str)

    loader = DataFrameLoader(dataframe, page_content_column="date")

    data = loader.load()

    buy_or_sell = ai_service.buy_or_sell({"data":data})

    ## 매도 신호가 왔을 때
    if buy_or_sell['result'] == "SELL":
        ## 현재 보유한 암호화폐가 없으면
        if crypto_service.get_balances(ticker) == 0:
            log.debug("""
            ================================== 
              ** 매도 결과 **                    
              보유한 암호화폐가 없음              
            ==================================  
            """)
        else:
            ## 이익 계산해보고 매도
            is_profit = crypto_service.calculate_profit({
                "ticker":ticker
            })
            if is_profit['result'] == "PROFIT":
                sell_result = crypto_service.do_sell({
                    "ticker":ticker,
                    "amount":crypto_service.get_balances(ticker)
                })
                log.debug(f"""
                ================================== 
                  ** 매도 결과 **                    
                $$  {sell_result}  $$              
                ==================================  
                """)



    ## 매수 신호가 왔을 떄
    if buy_or_sell['result'] == "BUY":
        ## 현재 보유한 암호화폐가 없으면
        if crypto_service.get_balances(ticker) == 0:
            buy_result = crypto_service.do_buy({
                "ticker":ticker,
                "amount": amount,
                "price": 6000
            })
            log.debug(f"""
            ================================== 
              ** 매수 결과 **                    
            $$  {buy_result} $$          
            ==================================  
            """)


# refresh_file()

while True:

    try :
        current_time = datetime.now()

        df = crypto_service.get_ema_data(ticker=ticker, interval="minutes60", count=120)

        stage_result = crypto_service.get_stage(df)
        stage = stage_result['stage']


        log.info(f"""
        ==================
        #                #
        #     {stage}     #
        #                #
        ==================
        """)

        result = crypto_service.stage_calling(stage)

        if crypto_service.get_balances(ticker) != 0:
            log.info(f"""
            =====================
            #                   #
            #    이익 추정 구간    #
            #                   #
            =====================
            """)
            is_profit = crypto_service.calculate_profit({
                "ticker": ticker
            })
            if is_profit['result'] == "PROFIT":
                sell_result = crypto_service.do_sell({
                    "ticker": ticker,
                    "amount": crypto_service.get_balances(ticker)
                })
                log.debug(f"""
                            ================================== 
                              ** 매도 결과 **                    
                            $$  {sell_result}  $$              
                            ==================================  
                            """)


        if result['result'] == "BUY_TRUE":
            log.info(f"""
            ==================
            #                #
            #   매수 신호    #
            #                #
            ==================
            """)
            main(stage_result['data'].tail(n=10))

        elif result['result'] == "SELL_TRUE":
            log.info(f"""
            ==================
            #                #
            #   매도 신호    #
            #                #
            ==================
            """)
            main(stage_result['data'].tail(n=10))
        else :
            pass

        # # 3 시간마다 로그 파일 , 데이터 파일 초기화
        if current_time - last_send_time >= timedelta(hours=3):
            send_log_file("로그 파일 초기화 전 백업")
            send_mail("데이터 파일 초기화 전 백업")

        last_send_time = current_time
    except Exception as err:
        log.error("=========================================")
        log.error(err)
        log.error("=========================================")
        pass

    time.sleep(65)