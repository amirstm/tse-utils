"""
This module holds tsetmc modules, which are mostly \
inherited from default models.
"""
from dataclasses import dataclass
from datetime import datetime, date, time
from tse_utils.models.enums import Nsc
from tse_utils.models import realtime, instrument


@dataclass
class InstrumentIdentification(instrument.InstrumentIdentification):
    """Identification information of an instrument"""
    market_code: int = None
    market_title: str = None
    sector_code: int = None
    sector_title: str = None
    sub_sector_code: int = None
    sub_sector_title: str = None
    type_id: int = None

    def __init__(self, tsetmc_code: str, tsetmc_raw_data: dict):
        self.market_title = tsetmc_raw_data["cgrValCotTitle"]
        self.market_code = tsetmc_raw_data["cComVal"]
        self.sector_code = int(
            tsetmc_raw_data["sector"]["cSecVal"].replace(" ", "")
        )
        self.sector_title = tsetmc_raw_data["sector"]["lSecVal"]
        if "subSector" in tsetmc_raw_data:
            self.sub_sector_code = tsetmc_raw_data["subSector"]["cSoSecVal"]
            self.sub_sector_title = tsetmc_raw_data["subSector"]["lSoSecVal"]
        self.type_id = int(tsetmc_raw_data["yVal"])
        instrument.InstrumentIdentification.__init__(
            self=self,
            tsetmc_code=tsetmc_code,
            isin=tsetmc_raw_data["instrumentID"],
            ticker=tsetmc_raw_data["lVal18AFC"],
            name_persian=tsetmc_raw_data["lVal30"],
            name_english=tsetmc_raw_data["lVal18"]
        )

    def __str__(self):
        return f"{self.ticker} [{self.isin}]"


@dataclass
class InstrumentSearchItem:
    """An item from the search results in TSETMC"""
    ticker: str = None
    name_persian: str = None
    tsetmc_code: str = None
    is_active: bool = None
    market_title: str = None

    def __init__(self, tsetmc_raw_data: dict):
        self.ticker = tsetmc_raw_data["lVal18AFC"]
        self.name_persian = tsetmc_raw_data["lVal30"]
        self.tsetmc_code = tsetmc_raw_data["insCode"]
        self.market_title = tsetmc_raw_data["flowTitle"]
        self.is_active = tsetmc_raw_data["lastDate"] != 0

    def __str__(self):
        return f"{self.ticker} <{self.tsetmc_code}>"


@dataclass
class ClosingPriceInfo(realtime.TradeCandle):
    """Holds realtime trade data of an instrument"""
    nsc: Nsc = None

    def __init__(self, tsetmc_raw_data: dict):
        self.nsc = Nsc[
            str(
                tsetmc_raw_data["instrumentState"]["cEtaval"]
            ).replace(" ", "")
        ]
        ltd_date = tsetmc_raw_data["finalLastDate"]
        ltd_time = tsetmc_raw_data["hEven"]
        last_trade_datetime = datetime(
            year=ltd_date // 10000, month=ltd_date // 100 % 100, day=ltd_date % 100,
            hour=ltd_time // 10000, minute=ltd_time // 100 % 100, second=ltd_time % 100
        )
        realtime.TradeCandle.__init__(
            self=self,
            previous_price=tsetmc_raw_data["priceYesterday"],
            open_price=tsetmc_raw_data["priceFirst"],
            last_price=tsetmc_raw_data["pDrCotVal"],
            close_price=tsetmc_raw_data["pClosing"],
            max_price=tsetmc_raw_data["priceMax"],
            min_price=tsetmc_raw_data["priceMin"],
            trade_num=tsetmc_raw_data["zTotTran"],
            trade_value=tsetmc_raw_data["qTotCap"],
            trade_volume=tsetmc_raw_data["qTotTran5J"],
            last_trade_datetime=last_trade_datetime
        )


@dataclass
class InstrumentInfo(InstrumentIdentification, realtime.BigQuantityParams):
    """Contains the instrument homepage data"""
    liquid_percentage: float = None
    average_trade_volume_monthly: int = None
    price_range_weekly: realtime.PriceRange = None
    price_range_annual: realtime.PriceRange = None
    price_thresholds: realtime.PriceRange = None

    def __init__(self, tsetmc_code: str, tsetmc_raw_data=dict):
        InstrumentIdentification.__init__(
            self=self,
            tsetmc_code=tsetmc_code,
            tsetmc_raw_data=tsetmc_raw_data
        )
        realtime.BigQuantityParams.__init__(
            self=self,
            base_volume=tsetmc_raw_data["baseVol"],
            total_shares=tsetmc_raw_data["zTitad"]
        )
        self.price_thresholds = realtime.PriceRange(
            max_price=tsetmc_raw_data["staticThreshold"]["psGelStaMax"],
            min_price=tsetmc_raw_data["staticThreshold"]["psGelStaMin"]
        )
        self.price_range_weekly = realtime.PriceRange(
            max_price=tsetmc_raw_data["maxWeek"],
            min_price=tsetmc_raw_data["minWeek"]
        )
        self.price_range_annual = realtime.PriceRange(
            max_price=tsetmc_raw_data["maxYear"],
            min_price=tsetmc_raw_data["minYear"]
        )
        self.average_trade_volume_monthly = tsetmc_raw_data["qTotTran5JAvg"]
        self.liquid_percentage = None \
            if len(tsetmc_raw_data["kAjCapValCpsIdx"]) == 0 \
            else float(tsetmc_raw_data["kAjCapValCpsIdx"])


@dataclass
class ClientType(realtime.ClientType):
    """ClientType data for an instrument"""

    def __init__(self, tsetmc_raw_data):
        realtime.ClientType.__init__(
            self=self,
            legal=realtime.ClientTypeTrade(
                buy=realtime.ClientTypeTradeQuantity(
                    num=tsetmc_raw_data["buy_CountN"],
                    volume=tsetmc_raw_data["buy_N_Volume"]
                ),
                sell=realtime.ClientTypeTradeQuantity(
                    num=tsetmc_raw_data["sell_CountN"],
                    volume=tsetmc_raw_data["sell_N_Volume"]
                )
            ),
            natural=realtime.ClientTypeTrade(
                buy=realtime.ClientTypeTradeQuantity(
                    num=tsetmc_raw_data["buy_CountI"],
                    volume=tsetmc_raw_data["buy_I_Volume"]
                ),
                sell=realtime.ClientTypeTradeQuantity(
                    num=tsetmc_raw_data["sell_CountI"],
                    volume=tsetmc_raw_data["sell_I_Volume"]
                )
            )
        )


@dataclass
class BestLimitsRow(realtime.OrderBookRow):
    """A single row from an instrument's order book"""

    def __init__(self, tsetmc_raw_data):
        realtime.OrderBookRow.__init__(
            self=self,
            demand=realtime.OrderBookRowSide(
                num=tsetmc_raw_data["zOrdMeDem"],
                volume=tsetmc_raw_data["qTitMeDem"],
                price=tsetmc_raw_data["pMeDem"]
            ),
            supply=realtime.OrderBookRowSide(
                num=tsetmc_raw_data["zOrdMeOf"],
                volume=tsetmc_raw_data["qTitMeOf"],
                price=tsetmc_raw_data["pMeOf"]
            )
        )


@dataclass
class BestLimits:
    """
    BestLimit is the same as OrderBook, contains an instrument's active orders
    """
    rows: list[BestLimitsRow] = None

    def __init__(self, tsetmc_raw_data):
        self.rows = [BestLimitsRow(x) for x in tsetmc_raw_data]


@dataclass
class ClosingPriceDaily(ClosingPriceInfo):
    def __init__(self, tsetmc_raw_data):
        self.close_price = tsetmc_raw_data["pClosing"]
        self.last_price = tsetmc_raw_data["pDrCotVal"]
        self.open_price = tsetmc_raw_data["priceFirst"]
        self.max_price = tsetmc_raw_data["priceMax"]
        self.min_price = tsetmc_raw_data["priceMin"]
        self.previous_price = tsetmc_raw_data["priceYesterday"]
        self.trade_value = tsetmc_raw_data["qTotCap"]
        self.trade_volume = tsetmc_raw_data["qTotTran5J"]
        self.trade_num = tsetmc_raw_data["zTotTran"]
        ltd_date = tsetmc_raw_data["dEven"]
        ltd_time = tsetmc_raw_data["hEven"]
        self.last_trade_datetime = datetime(
            year=ltd_date // 10000, month=ltd_date // 100 % 100, day=ltd_date % 100,
            hour=ltd_time // 10000, minute=ltd_time // 100 % 100, second=ltd_time % 100
        )


@dataclass
class ClientTypeDaily(ClientType):
    legal_buy_value: int = None
    legal_sell_value: int = None
    natural_buy_value: int = None
    natural_sell_value: int = None
    date: date = None

    def __init__(self, tsetmc_raw_data):
        self.legal_buy_num = tsetmc_raw_data["buy_N_Count"]
        self.legal_buy_value = tsetmc_raw_data["buy_N_Value"]
        self.legal_buy_volume = tsetmc_raw_data["buy_N_Volume"]
        self.legal_sell_num = tsetmc_raw_data["sell_N_Count"]
        self.legal_sell_value = tsetmc_raw_data["sell_N_Value"]
        self.legal_sell_volume = tsetmc_raw_data["sell_N_Volume"]
        self.natural_buy_num = tsetmc_raw_data["buy_I_Count"]
        self.natural_buy_value = tsetmc_raw_data["buy_I_Value"]
        self.natural_buy_volume = tsetmc_raw_data["buy_I_Volume"]
        self.natural_sell_num = tsetmc_raw_data["sell_I_Count"]
        self.natural_sell_value = tsetmc_raw_data["sell_I_Value"]
        self.natural_sell_volume = tsetmc_raw_data["sell_I_Volume"]
        rd_date = tsetmc_raw_data["recDate"]
        self.date = date(year=rd_date // 10000, month=rd_date //
                         100 % 100, day=rd_date % 100)


@dataclass
class TradeIntraday:
    price: int = None
    volume: int = None
    index: int = None
    time: time = None
    is_canceled: bool = None

    def __init__(self, tsetmc_raw_data):
        self.price = tsetmc_raw_data["pTran"]
        self.volume = tsetmc_raw_data["qTitTran"]
        self.index = tsetmc_raw_data["nTran"]
        h_even = tsetmc_raw_data["hEven"]
        self.time = time(
            hour=h_even // 10000, minute=h_even // 100 % 100, second=h_even % 100
        )
        self.is_canceled = bool(tsetmc_raw_data["canceled"])


@dataclass
class PriceAdjustment:
    date: date = None
    price_before: int = None
    price_after: int = None

    def __init__(self, tsetmc_raw_data):
        self.price_before = tsetmc_raw_data["pClosingNotAdjusted"]
        self.price_after = tsetmc_raw_data["pClosing"]
        d_even = tsetmc_raw_data["dEven"]
        self.date = date(
            year=d_even // 10000, month=d_even // 100 % 100, day=d_even % 100
        )


@dataclass
class InstrumentShareChange:
    date: date = None
    total_shares_before: int = None
    total_shares_after: int = None

    def __init__(self, tsetmc_raw_data):
        self.total_shares_before = tsetmc_raw_data["numberOfShareOld"]
        self.total_shares_after = tsetmc_raw_data["numberOfShareNew"]
        d_even = tsetmc_raw_data["dEven"]
        self.date = date(year=d_even // 10000, month=d_even //
                         100 % 100, day=d_even % 100)


@dataclass
class BestLimitsHistoryRow(BestLimitsRow):
    row_number: int = None
    time: time = None
    reference_id: int = None

    def __init__(self, tsetmc_raw_data, *args):
        self.row_number = tsetmc_raw_data["number"]
        self.reference_id = tsetmc_raw_data["refID"]
        h_even = tsetmc_raw_data["hEven"]
        self.time = time(
            hour=h_even // 10000, minute=h_even // 100 % 100, second=h_even % 100
        )
        super().__init__(tsetmc_raw_data=tsetmc_raw_data, *args)


@dataclass
class IndexDaily:
    date: date = None
    min_value: float = None
    max_value: float = None
    last_value: float = None

    def __init__(self, tsetmc_raw_data):
        self.min_value = tsetmc_raw_data["xNivInuPbMresIbs"]
        self.max_value = tsetmc_raw_data["xNivInuPhMresIbs"]
        self.last_value = tsetmc_raw_data["xNivInuClMresIbs"]
        d_even = tsetmc_raw_data["dEven"]
        self.date = date(
            year=d_even // 10000, month=d_even // 100 % 100, day=d_even % 100
        )


@dataclass
class InstrumentOptionInfo:
    tsetmc_code: str = None
    open_positions: int = None
    exercise_price: int = None
    exercise_date: date = None
    lot_size: int = None
    begin_date: date = None
    a_factor: float = None
    b_factor: float = None
    c_factor: float = None
    underlying_tsetmc_code: str = None

    def __init__(self, tsetmc_raw_data):
        self.tsetmc_code = tsetmc_raw_data["insCode"]
        self.open_positions = tsetmc_raw_data["buyOP"]
        self.exercise_price = tsetmc_raw_data["strikePrice"]
        end_date = tsetmc_raw_data["endDate"]
        self.exercise_date = date(
            year=end_date // 10000, month=end_date // 100 % 100, day=end_date % 100
        )
        begin_date = tsetmc_raw_data["beginDate"]
        self.begin_date = date(
            year=begin_date // 10000, month=begin_date // 100 % 100, day=begin_date % 100
        )
        self.lot_size = tsetmc_raw_data["contractSize"]
        self.a_factor = tsetmc_raw_data["aFactor"]
        self.b_factor = tsetmc_raw_data["bFactor"]
        self.c_factor = tsetmc_raw_data["cFactor"]
        self.underlying_tsetmc_code = tsetmc_raw_data["uaInsCode"]


@dataclass
class PrimaryMarketOverview:
    '''
    Contains data for the main (Bourse) market.
    '''
    index_last_value: int = None
    index_change: int = None
    index_equal_weighted_last_value: int = None
    index_equal_weighted_change: int = None
    datetime: datetime = None
    trade_value: int = None
    trade_volume: int = None
    trade_num: int = None
    market_state: str = None
    market_state_title: str = None
    market_value: int = None

    def __init__(self, tsetmc_raw_data):
        self.index_change = tsetmc_raw_data["indexChange"]
        self.index_equal_weighted_change = tsetmc_raw_data["indexEqualWeightedChange"]
        self.index_equal_weighted_last_value = tsetmc_raw_data["indexEqualWeightedLastValue"]
        self.index_last_value = tsetmc_raw_data["indexLastValue"]
        market_activity_deven = tsetmc_raw_data["marketActivityDEven"]
        market_activity_heven = tsetmc_raw_data["marketActivityHEven"]
        self.datetime = datetime(
            year=market_activity_deven // 10000, month=market_activity_deven // 100 % 100,
            day=market_activity_deven % 100, hour=market_activity_heven // 10000,
            minute=market_activity_heven // 100 % 100, second=market_activity_heven % 100
        )
        self.trade_value = tsetmc_raw_data["marketActivityQTotCap"]
        self.trade_volume = tsetmc_raw_data["marketActivityQTotTran"]
        self.trade_num = tsetmc_raw_data["marketActivityZTotTran"]
        self.market_state = tsetmc_raw_data["marketState"]
        self.market_state_title = tsetmc_raw_data["marketStateTitle"]
        self.market_value = tsetmc_raw_data["marketValue"]


@dataclass
class SecondaryMarketOverview:
    '''
    Contains data for the secondary and tertiary (FarBourse and Paye) market.
    '''
    index_last_value: int = None
    index_change: int = None
    datetime: datetime = None
    trade_value: int = None
    trade_volume: int = None
    trade_num: int = None
    market_state: str = None
    market_state_title: str = None
    market_value: int = None
    tertiary_market_value: int = None

    def __init__(self, tsetmc_raw_data):
        self.index_change = tsetmc_raw_data["indexChange"]
        self.index_last_value = tsetmc_raw_data["indexLastValue"]
        market_activity_deven = tsetmc_raw_data["marketActivityDEven"]
        market_activity_heven = tsetmc_raw_data["marketActivityHEven"]
        self.datetime = datetime(
            year=market_activity_deven // 10000, month=market_activity_deven // 100 % 100,
            day=market_activity_deven % 100, hour=market_activity_heven // 10000,
            minute=market_activity_heven // 100 % 100, second=market_activity_heven % 100
        )
        self.trade_value = tsetmc_raw_data["marketActivityQTotCap"]
        self.trade_volume = tsetmc_raw_data["marketActivityQTotTran"]
        self.trade_num = tsetmc_raw_data["marketActivityZTotTran"]
        self.market_state = tsetmc_raw_data["marketState"]
        self.market_state_title = tsetmc_raw_data["marketStateTitle"]
        self.market_value = tsetmc_raw_data["marketValue"]
        self.tertiary_market_value = tsetmc_raw_data["marketValueBase"]


@dataclass
class MarketWatchBestLimitsRow(BestLimitsRow):
    row_id: int = None

    def __init__(self, tsetmc_raw_data):
        self.demand_num = tsetmc_raw_data["zmd"]
        self.demand_volume = tsetmc_raw_data["qmd"]
        self.demand_price = tsetmc_raw_data["pmd"]
        self.supply_num = tsetmc_raw_data["zmo"]
        self.supply_volume = tsetmc_raw_data["qmo"]
        self.supply_price = tsetmc_raw_data["pmo"]
        self.row_id = tsetmc_raw_data["rid"]


@dataclass
class MarketWatchBestLimits:
    rows: list[MarketWatchBestLimitsRow] = None

    def __init__(self, tsetmc_raw_data):
        self.rows = [MarketWatchBestLimitsRow(x) for x in tsetmc_raw_data]


@dataclass
class MarketWatchTradeData(realtime.TradeCandle, instrument.InstrumentIdentification):
    last_trade_time: time = None
    max_price_threshold: int = None
    min_price_threshold: int = None
    eps: int = None
    total_shares: int = None
    base_volume: int = None
    best_limits: MarketWatchBestLimits = None

    def __init__(self, tsetmc_raw_data):
        self.tsetmc_code = tsetmc_raw_data["insCode"]
        self.ticker = tsetmc_raw_data["lva"]
        self.isin = tsetmc_raw_data["insID"]
        self.name_persian = tsetmc_raw_data["lvc"]
        self.total_shares = tsetmc_raw_data["ztd"]
        self.eps = tsetmc_raw_data["eps"]
        self.previous_price = tsetmc_raw_data["py"]
        self.last_price = tsetmc_raw_data["pdv"]
        self.open_price = tsetmc_raw_data["pf"]
        self.close_price = tsetmc_raw_data["pcl"]
        self.max_price_threshold = tsetmc_raw_data["pMax"]
        self.min_price_threshold = tsetmc_raw_data["pMin"]
        self.max_price = tsetmc_raw_data["pmx"]
        self.min_price = tsetmc_raw_data["pmn"]
        self.trade_value = tsetmc_raw_data["qtc"]
        self.trade_volume = tsetmc_raw_data["qtj"]
        self.trade_num = tsetmc_raw_data["ztt"]
        self.base_volume = tsetmc_raw_data["bv"]
        h_even = tsetmc_raw_data["hEven"]
        self.last_trade_time = time(
            hour=h_even//10000, minute=h_even//100 % 100, second=h_even % 100)
        self.best_limits = MarketWatchBestLimits(
            tsetmc_raw_data=tsetmc_raw_data["blDs"])


@dataclass
class MarketWatchClientTypeData(ClientType):
    tsetmc_code: str = None

    def __init__(self, tsetmc_raw_data):
        self.tsetmc_code = tsetmc_raw_data["insCode"]
        super().__init__(tsetmc_raw_data)


@dataclass
class TseClientInstrumentIdentity(InstrumentIdentification):
    last_change_date: date = None
    is_index: bool = None

    def __init__(self, tseclient_raw_data):
        self.tsetmc_code = tseclient_raw_data[0]
        self.isin = tseclient_raw_data[1]
        self.name_english = tseclient_raw_data[3]
        self.ticker = tseclient_raw_data[5]
        self.name_persian = tseclient_raw_data[6]
        self.type_id = int(tseclient_raw_data[17])
        sector_code = str(tseclient_raw_data[15]).replace(" ", "")
        if sector_code.isdigit():
            self.sector_code = int(sector_code)
            self.sub_sector_code = int(tseclient_raw_data[16])
            self.is_index = False
        else:
            self.is_index = True
        self.market_code = int(tseclient_raw_data[9])
        last_change_date_raw = int(tseclient_raw_data[8])
        self.last_change_date = date(
            year=last_change_date_raw//10000,
            month=last_change_date_raw//100 % 100,
            day=last_change_date_raw % 100
        )


class TsetmcScrapeException(Exception):
    """Tsetmc bad response status error."""

    def __init__(self, *args, **kwargs):
        self.status_code = kwargs.get('status_code')
        super().__init__(*args)
