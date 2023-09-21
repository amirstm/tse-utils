from dataclasses import dataclass
from datetime import datetime
import threading


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
        return self.legal_buy_volume + self.natural_buy_volume


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


@dataclass
class DeepOrderBookRow:
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
        with self._buy_rows_lock:
            row = next((x for x in self._buy_rows if x.price == price), None)
            if row:
                row.volume = volume
                row.num = num
            else:
                self._buy_rows.append(DeepOrderBookRow(
                    num=num, volume=volume, price=price))

    def update_sell_row(self, num: int, volume: int, price: int) -> None:
        with self._sell_rows_lock:
            row = next((x for x in self._sell_rows if x.price == price), None)
            if row:
                row.volume = volume
                row.num = num
            else:
                self._sell_rows.append(DeepOrderBookRow(
                    num=num, volume=volume, price=price))

    def remove_buy_row(self, price: int) -> None:
        with self._buy_rows_lock:
            row = next((x for x in self._buy_rows if x.price == price), None)
            if row:
                self._buy_rows.remove(row)

    def remove_sell_row(self, price: int) -> None:
        with self._sell_rows_lock:
            row = next((x for x in self._sell_rows if x.price == price), None)
            if row:
                self._sell_rows.remove(row)

    def empty_buy_rows(self) -> None:
        with self._buy_rows_lock:
            self._buy_rows.clear()

    def empty_sell_rows(self) -> None:
        with self._sell_rows_lock:
            self._sell_rows.clear()

    def get_buy_rows(self) -> list[DeepOrderBookRow]:
        with self._buy_rows_lock:
            return sorted(self._buy_rows.copy(), key=lambda x: x.price, reverse=True)

    def get_sell_rows(self) -> list[DeepOrderBookRow]:
        with self._sell_rows_lock:
            return sorted(self._sell_rows.copy(), key=lambda x: x.price, reverse=False)
