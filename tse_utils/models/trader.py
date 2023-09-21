from dataclasses import dataclass
from datetime import date, datetime
import threading
import logging
from abc import ABC, abstractmethod
from typing import Callable
from tse_utils.models.enums import TradeSide, TraderConnectionState, OrderLock, OrderState, OrderValidity
from tse_utils.models import instrument


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
            position = next(
                (x for x in self._positions if x.isin == isin), None)
            if position:
                self._positions.remove(position)

    def empty_position(self) -> None:
        with self._positions_lock:
            self._positions.clear()

    def update_position(self, isin: str, quantity: int, position_open_price: int = None,
                        instrument_last_price: int = None, instrument_close_price: int = None) -> None:
        with self._positions_lock:
            position = next(
                (x for x in self._positions if x.isin == isin), None)
            if position:
                position.quantity = quantity
                position.position_open_price = position_open_price
                position.instrument_close_price = instrument_close_price
                position.instrument_last_price = instrument_last_price
            else:
                self._positions.append(PortfolioSecurity(isin=isin, quantity=quantity, position_open_price=position_open_price,
                                                         instrument_close_price=instrument_close_price,
                                                         instrument_last_price=instrument_last_price))


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
    """
    display_name is used for logging purposes. If it is not set, username will be used insted.
    """
    display_name: str = None
    bourse_code: str = None
    oms_code: str = None

    def __str__(self) -> str:
        return self.display_name if self.display_name else self.username


@dataclass
class TradingAPI:
    broker_title: str = None
    oms_title: str = None
    oms_domain: str = None

    def __str__(self) -> str:
        return f"{self.oms_title} - {self.broker_title}"


class Trader(ABC):
    """
    Trader class holds the data for a single trader account and can be inheridated by classes specialized in training using a speicif OMS API.
    """

    def __init__(self, identification: TraderIdentification, api: TradingAPI, logger_name: str = None):
        self.identification = identification
        self.api = api
        self.logger = logging.getLogger(logger_name)
        self.connection_state: TraderConnectionState = TraderConnectionState.NO_LOGIN
        self.portfolio = Portfolio()
        self._orders: list[Order] = []
        self._orders_lock = threading.Lock()
        self._subscribed_instruments: list[instrument.Instrument] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            await self.disconnect()
        except Exception as ex:
            self.logger.error("Disconnect failed while disposing object.")
            self.logger.debug(
                "Encountered {0} when trying to disconnect.".format(ex))

    def __str__(self) -> str:
        return f"{str(self.identification)}@{self.api.broker_title}"

    def get_order(self, oms_id) -> Order:
        with self._orders_lock:
            return next((x for x in self._orders if x.oms_id == oms_id), None)

    def get_order_custom(self, filter_func: Callable[[Order], bool]) -> Order:
        with self._orders_lock:
            return next((x for x in self._orders if filter_func(x)), None)

    def get_orders(self, filter_func: Callable[[Order], bool] = lambda x: True) -> list[Order]:
        with self._orders_lock:
            return [x for x in self._orders if filter_func(x)]

    def remove_order(self, oms_id) -> None:
        with self._orders_lock:
            order = next((x for x in self._orders if x.oms_id == oms_id), None)
            if order:
                self._orders.remove(order)

    def empty_orders(self) -> None:
        with self._orders_lock:
            self._orders.clear()

    def add_order(self, order: Order) -> None:
        with self._orders_lock:
            self._orders.append(order)

    def get_subscribed_instrument(self, isin: str = None):
        return next((x for x in self._subscribed_instruments if x.identification.isin == isin), None)

    @abstractmethod
    async def connect(self) -> None:
        """
        Does a single attempt on logging in to the trader account
        """

    @abstractmethod
    async def connect_looper(self, interval: int = 3, max_trial=10) -> None:
        """
        Recursively trying to login to the trader account
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Logs of from the trader account
        """

    @abstractmethod
    async def get_server_datetime(self) -> datetime:
        """
        Gets server datetime
        """

    @abstractmethod
    async def pull_trader_data(self):
        """
        Fetches client data from OMS using a pull request
        """

    @abstractmethod
    async def subscribe_instruments_list(self, instruments: list[instrument.Instrument]):
        """
        Subscribes the instruments on the OMS pusher to get their realtime data
        """

    @abstractmethod
    async def order_send(
        self, side: TradeSide, isin: str, quantity: int, price: int, client_id: str = None,
        validity: OrderValidity = OrderValidity.DAY, expiration_date: date = None
    ):
        """
        Used for sending a new order to the OMS
        """

    @abstractmethod
    async def order_cancel(self, order: Order):
        """
        Used for canceling an active order
        """

    @abstractmethod
    async def order_edit(self, order: Order, quantity: int, price: int):
        """
        Used for editing an active order
        """
