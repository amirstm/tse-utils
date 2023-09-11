from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderBookRow():
    """
    Contains a single row from an instrument's order book
    """
    demand_num: int = 0
    demand_volume: int = 0
    demand_price: int = 0
    supply_num: int = 0
    supply_volume: int = 0
    supply_price: int = 0

    def __str__(self):
        return f"{self.supply_num} {self.supply_volume} {self.supply_price} | {self.demand_price} {self.demand_volume} {self.demand_num}"

@dataclass
class OrderBook():
    """
    Orderbook contains the top n rows of an instrument's orders on both sides.
    """
    def __init__(self, row_count: int = 5):
        self.rows = [OrderBookRow() for i in range(row_count)]
    
    # def get_diff(self): TODO: get difference with order

@dataclass
class ClientType():
    """
    ClientType holds data used to separate the share of the natural investors from the legal ones from trades
    """
    legal_buy_num: int = 0
    legal_buy_volume: int = 0
    legal_sell_num: int = 0
    legal_sell_volume: int = 0
    natural_buy_num: int = 0
    natural_buy_volume: int = 0
    natural_sell_num: int = 0
    natural_sell_volume: int = 0

    def trade_volume(self) -> int:
        return self.LegalBuyVolume + self.NaturalBuyVolume

@dataclass
class TradeCandle():
    previous_price: int = 0
    open_price: int = 0
    close_price: int = 0
    last_price: int = 0
    max_price: int = 0
    min_price: int = 0
    trade_num: int = 0
    trade_value: int = 0
    trade_volume: int = 0
    open_trade_datetime: datetime = None
    last_trade_datetime: datetime = None
