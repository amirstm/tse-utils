from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderBookRow():
    """
    Contains a single row from an instrument's order book
    """
    demand_num: int = None
    demand_volume: int = None
    demand_price: int = None
    supply_num: int = None
    supply_volume: int = None
    supply_price: int = None

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
    legal_buy_num: int = None
    legal_buy_volume: int = None
    legal_sell_num: int = None
    legal_sell_volume: int = None
    natural_buy_num: int = None
    natural_buy_volume: int = None
    natural_sell_num: int = None
    natural_sell_volume: int = None

    def trade_volume(self) -> int:
        return self.LegalBuyVolume + self.NaturalBuyVolume

@dataclass
class TradeCandle():
    previous_price: int = None
    open_price: int = None
    close_price: int = None
    last_price: int = None
    max_price: int = None
    min_price: int = None
    trade_num: int = None
    trade_value: int = None
    trade_volume: int = None
    open_trade_datetime: datetime = None
    last_trade_datetime: datetime = None
