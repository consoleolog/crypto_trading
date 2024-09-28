import time

from config import *


from langchain_community.document_loaders import DataFrameLoader

from service.mail_service import send_mail, send_log_file

from service import ai_service, crypto_service

from datetime import datetime, timedelta

from logger import log

ticker = TICKER

while True:

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

    if stage == "stage4" or stage == "stage5":
        if crypto_service.get_balances(ticker) == 0:
            buy_result = crypto_service.do_buy({
                "ticker":ticker,
                "amount": crypto_service.get_balances(ticker),
                "price": 6000
            })
            log.debug(f"""
            ================================== 
              ** 매수 결과 **                    
            $$  {buy_result} $$          
            ==================================  
            """)


    if crypto_service.get_balances(ticker) > 0:

        profit = crypto_service.get_profit({
            "ticker":ticker
        })

        log.info(f"""
        ========================================================================
        ** 이익률 **
        $$ {profit}     
        ========================================================================
        """)

        if profit > 0.6:
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




    time.sleep(5)
