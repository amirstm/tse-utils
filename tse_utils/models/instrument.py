"""
Gathers the classes from realtime and other instruments data \
to build complete instrument classes
"""
from dataclasses import dataclass
from abc import ABC
from datetime import date
from tse_utils.models.realtime import (
    OrderBook,
    ClientType,
    TradeCandle,
    DeepOrderBook,
    OrderLimitations,
    BigQuantityParams
)


@dataclass
class InstrumentIdentification:
    """
    Holds the identification for instruments.
    """
    # pylint: disable=invalid-name
    isin: str = None
    tsetmc_code: str = None
    ticker: str = None
    name_persian: str = None
    name_english: str = None
    is_obsolete: bool = False

    def __str__(self):
        return f"{self.ticker} [{self.isin}]"


@dataclass
class InstrumentRealtime(ABC):
    """Interface for Instrument class that contains the realtime data"""
    orderbook: OrderBook = None
    client_type: ClientType = None
    intraday_trade_candle: TradeCandle = None
    deep_orderbook: DeepOrderBook = None

    def __init__(self):
        self.orderbook = OrderBook()
        self.client_type = ClientType()
        self.intraday_trade_candle = TradeCandle()
        self.deep_orderbook = DeepOrderBook()


class Instrument(InstrumentRealtime):
    """
    Holds all available data for a specific tradable instrument.
    """

    def __init__(
        self,
        identification: InstrumentIdentification,
    ):
        self.identification: InstrumentIdentification = identification
        self.big_quantity_params: BigQuantityParams = BigQuantityParams()
        self.trade_limitations: OrderLimitations = OrderLimitations()
        super(InstrumentRealtime, self).__init__()

    def ticker_with_tsetmc_hyperlink(self) -> str:
        """
        Returns an HTML element containing a hyperlink to the TSETMC page for instrument.
        """
        return f"<a href=\"http://www.tsetmc.com/Loader.aspx?ParTree=151311\
            &i={self.identification.tsetmc_code}\">{self.identification.ticker}</a>"

    def has_buy_queue(self) -> bool:
        """Checks if instrument has a queue on the buy side"""
        return self.orderbook.rows[0].demand_price == self.trade_limitations.max_price_threshold

    def has_sell_queue(self) -> bool:
        """Checks if instrument has a queue on the sell side"""
        return self.orderbook.rows[0].supply_price == self.trade_limitations.min_price_threshold

    def __str__(self):
        return str(self.identification)


class DerivativeInstrument(Instrument):
    '''
    Derivative instrument contains a self.underlying that represents the underlying instrument.
    '''

    def __init__(self, underlying: Instrument, **kwargs):
        self.underlying = underlying
        super().__init__(**kwargs)


class OptionInstrument(DerivativeInstrument):
    """Holds data for option contract instruments"""

    def __init__(
            self,
            exercise_date: date,
            exercise_price: int,
            lot_size: int = None,
            **kwargs
    ):
        self.exercise_date = exercise_date
        self.exercise_price = exercise_price
        self.lot_size = lot_size
        super().__init__(**kwargs)


@dataclass
class IndexIdentification:
    """
    Holds the identification for an index, for example the overal index.
    """
    tsetmc_code: str = None
    persian_name: str = None

    def __str__(self) -> str:
        return f"{self.persian_name} [{self.tsetmc_code}]"


@dataclass
class Index:
    """
    Holds all available data for a specific index.
    """
    identification: IndexIdentification
    min_value: int
    max_value: int
    last_value: int

    def __str__(self) -> str:
        return f"{self.identification}"
