from repository.crypto_repository import CryptoRepository
from repository.trading_repository import TradingRepository
from service.ai_service import LLmService
from service.crypto_service import CryptoService
from service.mail_service import MailService
from service.trading_service import TradingService

def Factory(ticker):

    crypto_repository = CryptoRepository(ticker)
    trading_repository = TradingRepository(ticker)
    mail_service = MailService(ticker)
    llm_service = LLmService(ticker)
    crypto_service = CryptoService(ticker)
    trading_service = TradingService(
        ticker=ticker,
        crypto_repository=crypto_repository,
        trading_repository=trading_repository,
        mail_service=mail_service,
        crypto_service=crypto_service
    )

    return {
        "cryptoRepository": crypto_repository,
        "tradingRepository": trading_repository,
        "tradingService": trading_service,
        "cryptoService": crypto_service,
        "llmService": llm_service
    }





