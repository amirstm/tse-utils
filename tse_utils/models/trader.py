"""
This model contains classes that can be used as interfaces for \
implementing the trader classes in the future. Each trader instance \
is responsible for a single account in a specific broker and OMS.
"""
from dataclasses import dataclass
from datetime import date, datetime
import threading
import logging
from abc import ABC, abstractmethod
from typing import Callable
from tse_utils.models.enums import (
    TradeSide,
    TraderConnectionState,
    OrderLock,
    OrderState,
    OrderValidityType
)
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


@dataclass
class OrderIdentifier:
    """Holds the identifiers of an Order"""
    oms_id: str | int
    isin: str
    side: TradeSide
    client_id: str = None
    """
    client_id is used for mapping the order on the OMS side with the one sent by a client
    """
    hon: str = None
    """
    hon identifies the position of order in the market kernel
    """


@dataclass
class OrderStatus:
    """Contains both OrderState and OrderLock"""
    state: OrderState = None
    lock: OrderLock = None


@dataclass
class OrderQuantity:
    """Holds all quantity information for an order"""
    quantity: int
    remaining_quantity: int = None
    executed_quantity: int = None


@dataclass
class OrderValidity:
    """Contains validity type of order and expiration date, if appropriate"""
    validity_type: OrderValidityType = None
    creation_datetime: datetime = None
    expiration_date: date = None
    """
    expiration_date is used for orders validity of which are GOOD_TILL_DATE
    """


class Order(OrderIdentifier, OrderStatus, OrderQuantity, OrderValidity):
    """
    Holds data for a single order from a trader.
    """

    # pylint: disable=too-many-arguments
    # The following 6 parameters are the bare minimums \
    # with which an order is identified
    def __init__(
        self,
        oms_id,
        isin: str,
        side: TradeSide,
        quantity: int,
        price: int
    ):
        OrderIdentifier.__init__(
            self=self,
            oms_id=oms_id,
            side=side,
            isin=isin
        )
        OrderStatus.__init__(self=self)
        OrderQuantity.__init__(
            self=self,
            quantity=quantity
        )
        OrderValidity.__init__(self=self)
        self.price: int = price
        self.blocked_credit: int = None
        self._trades: list[MicroTrade] = []
        self._trades_lock: threading.Lock = threading.Lock()

    def add_trade(self, trade: MicroTrade) -> None:
        """Add new trade to the list of order trades"""
        with self._trades_lock:
            self._trades.append(trade)

    def get_trades(self) -> list[MicroTrade]:
        """Get a copy of the order's trades list"""
        with self._trades_lock:
            return self._trades.copy()

    def __str__(self) -> str:
        return f"{self.side}|{self.state}|{self.oms_id}|\
            {self.isin}|P:{self.price},Q:{self.quantity}"


@dataclass
class PortfolioCash:
    """Holds the cash and credit in an account's portfolio"""
    free_balance: int = None
    blocked_balance: int = None
    accounting_remain: int = None
    credit_limit: int = None

    def get_all_balance(self) -> int:
        """Get net balance of the account (without credit)"""
        return self.free_balance + self.blocked_balance


@dataclass
class PortfolioSecurity:
    """Holds data for a single security asset in the porfolio"""
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
    """A trader account's portfolio consisting of cash, securities, and positions"""

    def __init__(self):
        self.cash: PortfolioCash = PortfolioCash()
        """
        The assets list includes instruments in which having a net short position is unallowed.
        """
        self._assets: list[PortfolioSecurity] = []
        self._assets_lock = threading.Lock()
        """
        The positions list includes instruments in which \
        having a net short position is possible, such as options and futures.
        """
        self._positions: list[PortfolioSecurity] = []
        self._positions_lock = threading.Lock()

    def has_asset(self, isin: str) -> bool:
        """Checks if portfolio has any asset of a specific security"""
        with self._assets_lock:
            return any(x for x in self._assets if x.isin == isin)

    def get_asset(self, isin: str) -> PortfolioSecurity:
        """Get asset in the portfolio from a specific security"""
        with self._assets_lock:
            return next((x for x in self._assets if x.isin == isin), None)

    def get_asset_quantity(self, isin: str) -> int:
        """Get asset quantity in the portfolio from a specific security"""
        with self._assets_lock:
            return next((x.quantity for x in self._assets if x.isin == isin), 0)

    def get_all_assets(self) -> list[PortfolioSecurity]:
        """Get a copy of the assets list in the portfolio"""
        with self._assets_lock:
            return self._assets.copy()

    def remove_asset(self, isin: str) -> None:
        """Remove an asset from the portfolio"""
        with self._assets_lock:
            asset = next((x for x in self._assets if x.isin == isin), None)
            if asset:
                self._assets.remove(asset)

    def empty_asset(self) -> None:
        """Remove all assets from the portfolio"""
        with self._assets_lock:
            self._assets.clear()

    def update_asset(
            self,
            security: PortfolioSecurity
    ) -> None:
        """Updates a specific asset in the portfolio"""
        with self._assets_lock:
            asset = next(
                (x for x in self._assets if x.isin == security.isin), None)
            if asset:
                asset.quantity = security.quantity
                asset.position_open_price = security.position_open_price
                asset.instrument_close_price = security.instrument_close_price
                asset.instrument_last_price = security.instrument_last_price
            else:
                self._assets.append(
                    PortfolioSecurity(
                        isin=security.isin,
                        quantity=security.quantity,
                        position_open_price=security.position_open_price,
                        instrument_close_price=security.instrument_close_price,
                        instrument_last_price=security.instrument_last_price
                    ))

    def has_position(self, isin: str) -> bool:
        """Checks if portfolio has any position of a specific security"""
        with self._positions_lock:
            return any(
                x
                for x in self._positions
                if x.isin == isin
            )

    def get_position(self, isin: str) -> PortfolioSecurity:
        """Get position in the portfolio from a specific security"""
        with self._positions_lock:
            return next((x for x in self._positions if x.isin == isin), None)

    def get_position_quantity(self, isin: str) -> int:
        """Get position quantity in the portfolio from a specific security"""
        with self._positions_lock:
            return next((x.quantity for x in self._positions if x.isin == isin), 0)

    def get_all_positions(self) -> list[PortfolioSecurity]:
        """Get a copy of the positions list in the portfolio"""
        with self._positions_lock:
            return self._positions.copy()

    def remove_position(self, isin: str) -> None:
        """Remove a position from the portfolio"""
        with self._positions_lock:
            position = next(
                (x for x in self._positions if x.isin == isin), None)
            if position:
                self._positions.remove(position)

    def empty_position(self) -> None:
        """Remove all positions from the portfolio"""
        with self._positions_lock:
            self._positions.clear()

    def update_position(
            self,
            security: PortfolioSecurity
    ) -> None:
        """Updates a specific position in the portfolio"""
        with self._positions_lock:
            position = next(
                (x for x in self._positions if x.isin == security.isin), None)
            if position:
                position.quantity = security.quantity
                position.position_open_price = security.position_open_price
                position.instrument_close_price = security.instrument_close_price
                position.instrument_last_price = security.instrument_last_price
            else:
                self._positions.append(
                    PortfolioSecurity(
                        isin=security.isin,
                        quantity=security.quantity,
                        position_open_price=security.position_open_price,
                        instrument_close_price=security.instrument_close_price,
                        instrument_last_price=security.instrument_last_price
                    ))


@dataclass
class TradingAPI:
    """Each trading API consists of a single OMS and a single broker"""
    broker_title: str = None
    oms_title: str = None
    oms_domain: str = None

    def __str__(self) -> str:
        return f"{self.oms_title} - {self.broker_title}"


@dataclass
class TraderCredentials:
    """Holds the credentials of a single trader account"""
    api: TradingAPI
    username: str
    # password is optional since some APIs work with long-lived tokens
    password: str = None


@dataclass
class TraderIdentification:
    """Holds the identification of a single trader account"""
    dbid: int = None
    first_name: str = None
    last_name: str = None
    """
    display_name is used for logging purposes. If it is not set, username will be used.
    """
    display_name: str = None
    bourse_code: str = None
    oms_code: str = None

    def __str__(self) -> str:
        return self.display_name


@dataclass
class TraderRealtimeData:
    """
    Contains the realtime data for a single trader account.
    This data is mostly pushed through subscriptions to websockets.
    """
    portfolio: Portfolio
    _orders: list[Order]
    _orders_lock: threading.Lock
    _subscribed_instruments: list[instrument.Instrument]

    def __init__(self):
        self.portfolio: Portfolio = Portfolio()
        self._orders: list[Order] = []
        self._orders_lock: threading.Lock = threading.Lock()
        self._subscribed_instruments: list[instrument.Instrument] = []


class Trader(ABC, TraderRealtimeData):
    """
    Trader class holds the data for a single trader account \
    and can be inheridated by classes specialized in training \
    using a specific OMS API.
    """

    def __init__(
            self,
            credentials: TraderCredentials,
            logger_name: str = None
    ):
        self.credentials: TraderCredentials = credentials
        self.identification: TraderIdentification = TraderIdentification()
        self.logger: logging.Logger = logging.getLogger(logger_name)
        self.connection_state: TraderConnectionState = TraderConnectionState.NO_LOGIN
        TraderRealtimeData.__init__(self=self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            await self.disconnect()
        except Exception as ex:
            self.logger.error(
                "Disconnect failed on disposing object."
            )
            self.logger.debug(
                "Encountered %s when trying to disconnect.",
                ex
            )
            raise ex

    def __str__(self) -> str:
        name = self.identification.display_name \
            if self.identification.display_name \
            else self.credentials.username
        return f"{name}@{self.credentials.api.broker_title}"

    def get_order(self, oms_id) -> Order:
        """Searchs for an order in the orders list using its oms_id"""
        with self._orders_lock:
            return next((x for x in self._orders if x.oms_id == oms_id), None)

    def get_order_custom(
            self,
            filter_func: Callable[[Order], bool]
    ) -> Order:
        """Searchs for an order in the orders list using a custom filter"""
        with self._orders_lock:
            return next((x for x in self._orders if filter_func(x)), None)

    def get_orders(
            self,
            filter_func: Callable[[Order], bool] = lambda x: True
    ) -> list[Order]:
        """Searchs for all orders complying with a filter in the orders list"""
        with self._orders_lock:
            return [x for x in self._orders if filter_func(x)]

    def remove_order(self, oms_id) -> None:
        """Removes an order from the orders list using its oms_id"""
        with self._orders_lock:
            order = next((x for x in self._orders if x.oms_id == oms_id), None)
            if order:
                self._orders.remove(order)

    def empty_orders(self) -> None:
        """Removes all orders from the orders list"""
        with self._orders_lock:
            self._orders.clear()

    def add_order(self, order: Order) -> None:
        """
        Adds a new order to the orders list.
        This method should be used by data pushers and not by the client.
        Client can use order_send to send a new order.
        """
        with self._orders_lock:
            self._orders.append(order)

    def get_subscribed_instrument(self, isin: str = None):
        """Gets a subscribed instrument from the subscribed instruments list"""
        return next((
            x
            for x in self._subscribed_instruments
            if x.identification.isin == isin
        ), None)

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
    async def subscribe_instruments_list(
        self,
        instruments: list[instrument.Instrument]
    ):
        """
        Subscribes the instruments on the OMS pusher to get their realtime data
        """

    @abstractmethod
    async def order_send(
        self,
        order: Order
    ):
        """
        Used for sending a new order to the OMS. 
        The input order object should be used as a data transfer object \
        and is not added to the orders list, since new orders to be added \
        there should come from the OMS pushers.
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
