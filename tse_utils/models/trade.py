from dataclasses import dataclass
from tse_utils.models.enums import *
from datetime import time, date, datetime
import threading

@dataclass
class TraderIdentification:
    """
    Holds the identification for a trader.
    """
    id: int = None
    username: str = None
    password: str = None
    first_name: str = None
    last_name: str = None

    def __str__(self):
        return f"{self.username}"

@dataclass
class MicroTrade:
    """
    Holds data for a single micro trade.
    """
    id = None
    isin: str = None
    side: TradeSide = None
    quantity: int = None
    price: int = None
    datetime: datetime = None
    htn: str = None

class Order:
    """
    Holds data for a single order from a trader.
    """
    def __init__(self, oms_id, isin: str, side: TradeSide, quantity: int = None, price: int = None,
                 remaining_quantity: int = None, executed_quantity: int = None, state: OrderState = None,
                 client_id: str = None, hon: str = None, blocked_credit: int = None, creation_datetime: datetime = None,
                 validity: OrderValidity = None, expiration_date: date = None, lock: OrderLock = None):
        self.oms_id = oms_id
        self.isin = isin
        self.side = side
        self.quantity = quantity
        self.price = price
        self.remaining_quantity = remaining_quantity
        self.executed_quantity = executed_quantity
        self.state = state
        """
        client_id is used for mapping the order on the OMS side with the one sent by a client.
        """
        self.client_id = client_id
        self.hon = hon
        self.blocked_credit = blocked_credit
        self.creation_datetime = creation_datetime
        self.validity = validity
        """
        expiration_date is used for orders validity of which are GOOD_TILL_DATE
        """
        self.expiration_date = expiration_date
        self.lock = lock
        self._trades: list[MicroTrade] = []
        self._trades_lock: threading.Lock = threading.Lock()

    def add_trade(self, trade: MicroTrade):
        with self._trades_lock:
            self._trades.append(trade)

    def get_trades(self):
        with self._trades_lock:
            return self._trades.copy()

    def __str__(self):
        return f"{self.side}|{self.state}|{self.oms_id}|{self.isin}|P:{self.price},Q:{self.quantity}"



