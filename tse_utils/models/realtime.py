"""
Realtime data for instruments are of different types
Classes in the realtime module holds such data
"""
from dataclasses import dataclass
from datetime import datetime
import threading
from tse_utils.models.enums import Nsc


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
        return f"{self.supply_num} {self.supply_volume} {self.supply_price} | \
            {self.demand_price} {self.demand_volume} {self.demand_num}"


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
    ClientType holds data used to separate the share of the natural investors \
    from the legal ones on trades
    """
    # pylint: disable=too-many-instance-attributes
    # The variables of client type are 2*2*2 and 8 is logical in this case
    legal_buy_num: int = None
    legal_buy_volume: int = None
    legal_sell_num: int = None
    legal_sell_volume: int = None
    natural_buy_num: int = None
    natural_buy_volume: int = None
    natural_sell_num: int = None
    natural_sell_volume: int = None

    def trade_volume(self) -> int:
        """returns total trade volume"""
        return self.legal_buy_volume + self.natural_buy_volume


@dataclass
class PriceRange:
    """Holds price thresholds"""
    max_price: int = None
    min_price: int = None


@dataclass
class TradeQuantity:
    """Holds trade quantity identifiers"""
    trade_num: int = None
    trade_value: int = None
    trade_volume: int = None


@dataclass
class TradeCandle(PriceRange, TradeQuantity):
    """Holds current or point in time trade data for an instrument"""
    previous_price: int = None
    open_price: int = None
    close_price: int = None
    last_price: int = None
    open_trade_datetime: datetime = None
    last_trade_datetime: datetime = None


@dataclass
class DeepOrderBookRow:
    """Deep and complete order book for an instrument"""
    num: int
    volume: int
    price: int

    def __str__(self) -> str:
        return f"{self.volume} @ {self.price}"


class DeepOrderBook:
    """
    DeepOrderbook contains all rows of an instrument's orders on both sides.
    """

    def __init__(self):
        self._buy_rows: list[DeepOrderBookRow] = []
        self._buy_rows_lock: threading.Lock = threading.Lock()
        self._sell_rows: list[DeepOrderBookRow] = []
        self._sell_rows_lock: threading.Lock = threading.Lock()

    def update_buy_row(self, num: int, volume: int, price: int) -> None:
        """Updates a single buy row if exists and adds it if not"""
        with self._buy_rows_lock:
            row = next((x for x in self._buy_rows if x.price == price), None)
            if row:
                row.volume = volume
                row.num = num
            else:
                self._buy_rows.append(DeepOrderBookRow(
                    num=num, volume=volume, price=price))

    def update_sell_row(self, num: int, volume: int, price: int) -> None:
        """Updates a single sell row if exists and adds it if not"""
        with self._sell_rows_lock:
            row = next((x for x in self._sell_rows if x.price == price), None)
            if row:
                row.volume = volume
                row.num = num
            else:
                self._sell_rows.append(DeepOrderBookRow(
                    num=num, volume=volume, price=price))

    def remove_buy_row(self, price: int) -> None:
        """Removes a single buy row"""
        with self._buy_rows_lock:
            row = next((x for x in self._buy_rows if x.price == price), None)
            if row:
                self._buy_rows.remove(row)

    def remove_sell_row(self, price: int) -> None:
        """Removes a single sell row"""
        with self._sell_rows_lock:
            row = next((x for x in self._sell_rows if x.price == price), None)
            if row:
                self._sell_rows.remove(row)

    def empty_buy_rows(self) -> None:
        """Removes all buy rows"""
        with self._buy_rows_lock:
            self._buy_rows.clear()

    def empty_sell_rows(self) -> None:
        """Removes all sell rows"""
        with self._sell_rows_lock:
            self._sell_rows.clear()

    def get_buy_rows(self) -> list[DeepOrderBookRow]:
        """Returns a copy of all buy rows"""
        with self._buy_rows_lock:
            return sorted(self._buy_rows.copy(), key=lambda x: x.price, reverse=True)

    def get_sell_rows(self) -> list[DeepOrderBookRow]:
        """Returns a copy of all sell rows"""
        with self._sell_rows_lock:
            return sorted(self._sell_rows.copy(), key=lambda x: x.price, reverse=False)


@dataclass
class OrderPriceLimitations(PriceRange):
    """Holds limitations on prices that mostly change daily"""
    price_tick: int = 1


@dataclass
class OrderQuantityLimitations:
    """Holds limitations on quantity of orders"""
    max_buy_order_quantity: int = None
    max_sell_order_quantity: int = None
    lot_size: int = 1


@dataclass
class OrderLimitations(
    OrderPriceLimitations,
    OrderQuantityLimitations
):
    """Holds the daily limitations for trading on instrument"""
    nsc: Nsc = None


@dataclass
class BigQuantityParams:
    """Holds big quantity parameters for instrument"""
    base_volume: int = 1
    total_shares: int = None
