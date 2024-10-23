from main import get_models
from trading_application import TradingApplication

ticker = "EGLD"

app = TradingApplication(ticker)

app.common_util.init()

models = get_models(app, ticker)