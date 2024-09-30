from dependency_injector import containers, providers

from repository.crypto_repository import CryptoRepository
from service.crypto_service import CryptoService
from service.ai_service import LLmService
from service.mail_service import MailService


from dependency_injector.wiring import Provide, inject
from langchain_community.document_loaders import DataFrameLoader

from logger import log


class CryptoApplication(containers.DeclarativeContainer):

    config = providers.Configuration()

    crypto_repository = providers.Factory(CryptoRepository)

    llm_service = providers.Factory(LLmService)

    mail_service = providers.Factory(MailService)

    crypto_service = providers.Factory(
        CryptoService,
        crypto_repository=crypto_repository,
        llm_service=llm_service,
        mail_service=mail_service
    )

@inject
def main(dataframe,
         llm_service=Provide[CryptoApplication.llm_service],
         crypto_service=Provide[CryptoApplication.crypto_service], ):
    dataframe = dataframe.copy()
    dataframe['date'] = dataframe['date'].astype(str)

    loader = DataFrameLoader(dataframe, page_content_column="date")

    data = loader.load()

    buy_or_sell = llm_service.buy_or_sell({"data": data})

    if buy_or_sell['result'] == "SELL":
        if crypto_service.get_balances() == 0:
            log.debug("""
            ================================== 
              ** 매도 결과 **                    
              보유한 암호화폐가 없음              
            ==================================  
            """)
        else:
            profit = crypto_service.get_profit()
            if profit > 0.6:
                crypto_service.do_sell({"amount": crypto_service.get_balances()})
    if buy_or_sell['result'] == "BUY":
        if crypto_service.get_balances() == 0:
            crypto_service.do_buy({
                "amount": crypto_service.get_balances(),
                "price": 6000
            })

def App():
    app = CryptoApplication()

    crypto_service = app.crypto_service()
    llm_service = app.llm_service()

    df = crypto_service.get_ema_data("minutes60", 120)

    stage_result = crypto_service.get_stage(df)

    stage = stage_result['stage']

    log.info(f"""
    ==================
    #     {stage}     #
    ==================
    """)

    if crypto_service.get_balances() != 0:
        log.info(f"""
        =====================
        #   이익 추정 구간  #   
        =====================
        """)
        profit = crypto_service.get_profit()
        log.info(f"""
        ====================================================
        ** 이익률 **
        $$ {profit}     
        ====================================================
        """)

        if profit > 0.6 :
             crypto_service.do_sell({
                "amount":crypto_service.get_balances()
            })

        result = crypto_service.stage_calling(stage)

        if result['result'] == "BUY_TRUE":
            log.info(f"""
            ==================
            #   매수 신호    #   
            ==================
            """)
            main(dataframe=df,
                 llm_service=llm_service,
                 crypto_service=crypto_service
            )

        if result['result'] == "SELL_TRUE":
            log.info(f"""
            ==================
            #   매도 신호    #
            ==================
            """)
            main(dataframe=df,
                 llm_service=llm_service,
                 crypto_service=crypto_service
            )