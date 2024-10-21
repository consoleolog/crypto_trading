from typing import Union


class Trade:
    def __init__(self, data:dict[str, Union[int, str]]):
        self.create_time = data["created_at"]
        self.ticker = data["market"]
        self.price = data["locked"]
        self.market_price = data["market_price"]