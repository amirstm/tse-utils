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

    def __str__(self) -> str:
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

    def add_trade(self, trade: MicroTrade) -> None:
        with self._trades_lock:
            self._trades.append(trade)

    def get_trades(self) -> list[MicroTrade]:
        with self._trades_lock:
            return self._trades.copy()

    def __str__(self) -> str:
        return f"{self.side}|{self.state}|{self.oms_id}|{self.isin}|P:{self.price},Q:{self.quantity}"

@dataclass
class PortfolioCash:
    free_balance: int = None
    blocked_balance: int = None
    accounting_remain: int = None
    credit_limit: int = None

    def get_all_balance(self) -> int:
        return self.free_balance + self.blocked_balance

@dataclass
class PortfolioSecurity:
    isin: str
    """
    positive quantity means a long position and a negative ones means a short position.
    """
    quantity: int = None
    position_open_price: int = None
    instrument_last_price: int = None
    instrument_close_price: int = None

    def __str__(self) -> str:
        return f"{self.quantity} of {self.isin}"
    
class Portfolio:

    def __init__(self):
        self.cash: PortfolioCash = PortfolioCash()
        """
        The assets list includes instruments in which having a net short position is unallowed.
        """
        self._assets: list[PortfolioSecurity] = []
        self._assets_lock = threading.Lock()
        """
        The positions list includes instruments in which having a net short position is possible, such as options and futures.
        """
        self._positions: list[PortfolioSecurity] = []
        self._positions_lock = threading.Lock()

    def has_asset(self, isin: str) -> bool:
        with self._assets_lock:
            return any(x for x in self._assets if x.isin == isin)
        
    def get_asset(self, isin: str) -> PortfolioSecurity:
        with self._assets_lock:
            return next((x for x in self._assets if x.isin == isin), None)

    def get_asset_quantity(self, isin: str) -> int:
        with self._assets_lock:
            return next((x.quantity for x in self._assets if x.isin == isin), 0)

    def get_all_assets(self) -> list[PortfolioSecurity]:
        with self._assets_lock:
            return self._assets.copy()

    def remove_asset(self, isin: str) -> None:
        with self._assets_lock:
            asset = next((x for x in self._assets if x.isin == isin), None)
            if asset:
                self._assets.remove(asset)

    def empty_asset(self) -> None:
        with self._assets_lock:
            self._assets.clear()

    def update_asset(self, isin: str, quantity: int, position_open_price: int = None,
                    instrument_last_price: int = None, instrument_close_price: int = None) -> None:
        with self._assets_lock:
            asset = next((x for x in self._assets if x.isin == isin), None)
            if asset:
                asset.quantity = quantity
                asset.position_open_price = position_open_price
                asset.instrument_close_price = instrument_close_price
                asset.instrument_last_price = instrument_last_price
            else:
                self._assets.append(PortfolioSecurity(isin=isin, quantity=quantity, position_open_price=position_open_price,
                                                      instrument_close_price=instrument_close_price, 
                                                      instrument_last_price=instrument_last_price))
    
    def has_position(self, isin: str) -> bool:
        with self._positions_lock:
            return any(x for x in self._positions if x.isin == isin)
        
    def get_position(self, isin: str) -> PortfolioSecurity:
        with self._positions_lock:
            return next((x for x in self._positions if x.isin == isin), None)

    def get_position_quantity(self, isin: str) -> int:
        with self._positions_lock:
            return next((x.quantity for x in self._positions if x.isin == isin), 0)

    def get_all_positions(self) -> list[PortfolioSecurity]:
        with self._positions_lock:
            return self._positions.copy()

    def remove_position(self, isin: str) -> None:
        with self._positions_lock:
            position = next((x for x in self._positions if x.isin == isin), None)
            if position:
                self._positions.remove(position)

    def empty_position(self) -> None:
        with self._positions_lock:
            self._positions.clear()

    def update_position(self, isin: str, quantity: int, position_open_price: int = None,
                    instrument_last_price: int = None, instrument_close_price: int = None) -> None:
        with self._positions_lock:
            position = next((x for x in self._positions if x.isin == isin), None)
            if position:
                position.quantity = quantity
                position.position_open_price = position_open_price
                position.instrument_close_price = instrument_close_price
                position.instrument_last_price = instrument_last_price
            else:
                self._positions.append(PortfolioSecurity(isin=isin, quantity=quantity, position_open_price=position_open_price,
                                                      instrument_close_price=instrument_close_price, 
                                                      instrument_last_price=instrument_last_price))
    

