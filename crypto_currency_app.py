from config import Provider
from repository.crypto_currency_repository import CryptoCurrencyRepository
from service.crypto_currency_service import CryptoCurrencyService
from service.mail_service import MailService


class CryptoCurrencyApplication:
    def __init__(self, ticker):

        self.__provider = Provider(ticker)

        self.__crypto_currency_repository = CryptoCurrencyRepository(
            provider=self.__provider
        )

        self.__mail_service = MailService(
            provider=self.__provider
        )

        self.__crypto_currency_service = CryptoCurrencyService(
            provider=self.__provider,
            mail_service=self.__mail_service,
            crypto_currency_repository=self.__crypto_currency_repository
        )


    @property
    def crypto_currency_service(self):
        return self.__crypto_currency_service

