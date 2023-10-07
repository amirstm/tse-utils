"""
Realtime data for instruments are of different types
Classes in the realtime module holds such data
"""
from dataclasses import dataclass
from datetime import datetime
import threading
from tse_utils.models.enums import Nsc


@dataclass
class OrderBookRowSide:
    """A single side on a row of an instrument's order book"""
    num: int = 0
    volume: int = 0
    price: int = 0

    def __str__(self) -> str:
        return f"{self.volume} @ {self.price}"


@dataclass
class OrderBookRow():
    """
    Contains a single row from an instrument's order book
    """
    demand: OrderBookRowSide
    supply: OrderBookRowSide

    def __init__(
            self,
            demand: OrderBookRowSide = None,
            supply: OrderBookRowSide = None
    ):
        self.demand = demand if demand else OrderBookRowSide()
        self.supply = supply if supply else OrderBookRowSide()

    def __str__(self):
        return f"{self.supply.num} {self.supply.volume} {self.supply.price} | \
            {self.demand.price} {self.demand.volume} {self.demand.num}"


@dataclass
class OrderBook():
    """
    Orderbook contains the top n rows of an instrument's orders on both sides.
    """

    def __init__(self, row_count: int = 5):
        self.rows = [OrderBookRow() for i in range(row_count)]

    # def get_diff(self): TODO: get difference with order


@dataclass
class ClientTypeTradeQuantity:
    """Holds trade quantity for a single side of a single type of client"""
    num: int = None
    volume: int = None
    # In many cases the value parameter is not valued
    value: int = None


@dataclass
class ClientTypeTrade:
    """Holds trades for a single type of client"""
    buy: ClientTypeTradeQuantity
    sell: ClientTypeTradeQuantity

    def __init__(
            self,
            buy: ClientTypeTradeQuantity = None,
            sell: ClientTypeTradeQuantity = None
    ):
        self.buy = buy if buy else ClientTypeTradeQuantity()
        self.sell = sell if sell else ClientTypeTradeQuantity()


@dataclass
class ClientType:
    """
    ClientType holds data used to separate the share of the natural investors \
    from the legal ones on trades
    """
    legal: ClientTypeTrade
    natural: ClientTypeTrade

    def __init__(
            self,
            legal: ClientTypeTrade = None,
            natural: ClientTypeTrade = None
    ):
        self.legal = legal if legal else ClientTypeTrade()
        self.natural = natural if natural else ClientTypeTrade()

    def trade_volume(self) -> int:
        """returns total trade volume"""
        return self.legal.buy.volume + self.natural.buy.volume


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


class DeepOrderBook:
    """
    DeepOrderbook contains all rows of an instrument's orders on both sides.
    """

    def __init__(self):
        self._buy_rows: list[OrderBookRowSide] = []
        self._buy_rows_lock: threading.Lock = threading.Lock()
        self._sell_rows: list[OrderBookRowSide] = []
        self._sell_rows_lock: threading.Lock = threading.Lock()

    def update_buy_row(self, num: int, volume: int, price: int) -> None:
        """Updates a single buy row if exists and adds it if not"""
        with self._buy_rows_lock:
            row = next((x for x in self._buy_rows if x.price == price), None)
            if row:
                row.volume = volume
                row.num = num
            else:
                self._buy_rows.append(OrderBookRowSide(
                    num=num, volume=volume, price=price))

    def update_sell_row(self, num: int, volume: int, price: int) -> None:
        """Updates a single sell row if exists and adds it if not"""
        with self._sell_rows_lock:
            row = next((x for x in self._sell_rows if x.price == price), None)
            if row:
                row.volume = volume
                row.num = num
            else:
                self._sell_rows.append(OrderBookRowSide(
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

    def get_buy_rows(self) -> list[OrderBookRowSide]:
        """Returns a copy of all buy rows"""
        with self._buy_rows_lock:
            return sorted(self._buy_rows.copy(), key=lambda x: x.price, reverse=True)

    def get_sell_rows(self) -> list[OrderBookRowSide]:
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
