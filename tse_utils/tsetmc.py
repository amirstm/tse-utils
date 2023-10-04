"""
This module uses httpx to fetch data asynchronously \
from the TSETMC website. 
"""
import json
from dataclasses import dataclass
from datetime import datetime, date, time
import httpx
from bs4 import BeautifulSoup
from tse_utils.exceptions import MyProjectError
from tse_utils.models.enums import Nsc
from tse_utils.models import realtime, instrument


@dataclass
class InstrumentIdentity(instrument.InstrumentIdentification):
    market_code: int = None
    market_title: str = None
    sector_code: int = None
    sector_title: str = None
    sub_sector_code: int = None
    sub_sector_title: str = None
    type_id: int = None

    def __init__(self, tsetmc_raw_data):
        self.isin = tsetmc_raw_data["instrumentID"]
        self.name_english = tsetmc_raw_data["lVal18"]
        self.name_persian = tsetmc_raw_data["lVal30"]
        self.ticker = tsetmc_raw_data["lVal18AFC"]
        self.market_title = tsetmc_raw_data["cgrValCotTitle"]
        self.market_code = tsetmc_raw_data["cComVal"]
        self.sector_code = int(
            tsetmc_raw_data["sector"]["cSecVal"].replace(" ", ""))
        self.sector_title = tsetmc_raw_data["sector"]["lSecVal"]
        self.sub_sector_code = tsetmc_raw_data["subSector"]["cSoSecVal"]
        self.sub_sector_title = tsetmc_raw_data["subSector"]["lSoSecVal"]
        self.type_id = int(tsetmc_raw_data["yVal"])

    def __str__(self):
        return f"{self.ticker} [{self.isin}]"


@dataclass
class InstrumentSearchItem:
    ticker: str = None
    name_persian: str = None
    tsetmc_code: str = None
    is_active: bool = None
    market_title: str = None

    def __init__(self, tsetmc_raw_data):
        self.ticker = tsetmc_raw_data["lVal18AFC"]
        self.name_persian = tsetmc_raw_data["lVal30"]
        self.tsetmc_code = tsetmc_raw_data["insCode"]
        self.market_title = tsetmc_raw_data["flowTitle"]
        self.is_active = tsetmc_raw_data["lastDate"] != 0

    def __str__(self):
        return f"{self.ticker} <{self.tsetmc_code}>"


@dataclass
class ClosingPriceInfo(realtime.TradeCandle):
    nsc: Nsc = None

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
        self.nsc = Nsc[str(tsetmc_raw_data["instrumentState"]
                           ["cEtaval"]).replace(" ", "")]
        ltd_date = tsetmc_raw_data["finalLastDate"]
        ltd_time = tsetmc_raw_data["hEven"]
        self.last_trade_datetime = datetime(
            year=ltd_date // 10000, month=ltd_date // 100 % 100, day=ltd_date % 100,
            hour=ltd_time // 10000, minute=ltd_time // 100 % 100, second=ltd_time % 100
        )


@dataclass
class InstrumentInfo(InstrumentIdentity):
    base_volume: int = None
    liquid_percentage: float = None
    max_price_weekly: int = None
    min_price_weekly: int = None
    max_price_annual: int = None
    min_price_annual: int = None
    average_trade_volume_monthly: int = None
    total_shares: int = None
    max_price_threshold: int = None
    min_price_threshold: int = None

    def __init__(self, tsetmc_raw_data):
        self.isin = tsetmc_raw_data["instrumentID"]
        self.name_english = tsetmc_raw_data["lVal18"]
        self.name_persian = tsetmc_raw_data["lVal30"]
        self.ticker = tsetmc_raw_data["lVal18AFC"]
        self.market_title = tsetmc_raw_data["cgrValCotTitle"]
        self.market_code = int(tsetmc_raw_data["cComVal"])
        self.type_id = int(tsetmc_raw_data["yVal"])
        self.base_volume = tsetmc_raw_data["baseVol"]
        self.total_shares = tsetmc_raw_data["zTitad"]
        self.max_price_threshold = tsetmc_raw_data["staticThreshold"]["psGelStaMax"]
        self.min_price_threshold = tsetmc_raw_data["staticThreshold"]["psGelStaMin"]
        self.max_price_weekly = tsetmc_raw_data["maxWeek"]
        self.min_price_weekly = tsetmc_raw_data["minWeek"]
        self.max_price_annual = tsetmc_raw_data["maxYear"]
        self.min_price_annual = tsetmc_raw_data["minYear"]
        self.average_trade_volume_monthly = tsetmc_raw_data["qTotTran5JAvg"]
        self.liquid_percentage = None if len(
            tsetmc_raw_data["kAjCapValCpsIdx"]) == 0 else float(tsetmc_raw_data["kAjCapValCpsIdx"])


@dataclass
class ClientType(realtime.ClientType):
    def __init__(self, tsetmc_raw_data):
        self.legal_buy_num = tsetmc_raw_data["buy_CountN"]
        self.legal_buy_volume = tsetmc_raw_data["buy_N_Volume"]
        self.legal_sell_num = tsetmc_raw_data["sell_CountN"]
        self.legal_sell_volume = tsetmc_raw_data["sell_N_Volume"]
        self.natural_buy_num = tsetmc_raw_data["buy_CountI"]
        self.natural_buy_volume = tsetmc_raw_data["buy_I_Volume"]
        self.natural_sell_num = tsetmc_raw_data["sell_CountI"]
        self.natural_sell_volume = tsetmc_raw_data["sell_I_Volume"]


@dataclass
class BestLimitsRow(realtime.OrderBookRow):
    def __init__(self, tsetmc_raw_data):
        self.demand_num = tsetmc_raw_data["zOrdMeDem"]
        self.demand_volume = tsetmc_raw_data["qTitMeDem"]
        self.demand_price = tsetmc_raw_data["pMeDem"]
        self.supply_num = tsetmc_raw_data["zOrdMeOf"]
        self.supply_volume = tsetmc_raw_data["qTitMeOf"]
        self.supply_price = tsetmc_raw_data["pMeOf"]


@dataclass
class BestLimits:
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
class TseClientInstrumentIdentity(InstrumentIdentity):
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


class TsetmcScrapeError(MyProjectError):
    """Tsetmc bad response status error."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.status_code = kwargs.get('status_code')


class TsetmcScraper():
    """
    This class fetches data from tsetmc.com, the official website 
    for Tehran Stock Exchange market data.
    """

    def __init__(self, tsetmc_domain: str = "cdn.tsetmc.com"):
        self.tsetmc_domain = tsetmc_domain
        self.__client = httpx.AsyncClient(headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/89.0.4389.114 Safari/537.36",
            "accept": "application/json, text/plain, */*"
        }, base_url=f"http://{tsetmc_domain}/")

    async def __aenter__(self):
        return self

    async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback
    ):
        await self.__client.aclose()

    async def get_instrument_identity_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentIdentity/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_instrument_identity(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> InstrumentIdentity:
        raw = await self.get_instrument_identity_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return InstrumentIdentity(tsetmc_raw_data=raw["instrumentIdentity"])

    async def get_instrument_search_raw(
            self,
            search_value: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentSearch/{search_value}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_instrument_search(
            self,
            search_value: str,
            timeout: int = 3
    ) -> list[InstrumentSearchItem]:
        raw = await self.get_instrument_search_raw(
            search_value=search_value,
            timeout=timeout
        )
        return [InstrumentSearchItem(x) for x in raw["instrumentSearch"]]

    async def get_closing_price_info_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/ClosingPrice/GetClosingPriceInfo/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_closing_price_info(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> ClosingPriceInfo:
        raw = await self.get_closing_price_info_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return ClosingPriceInfo(tsetmc_raw_data=raw["closingPriceInfo"])

    async def get_instrument_info_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentInfo/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_instrument_info(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> InstrumentInfo:
        raw = await self.get_instrument_info_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return InstrumentInfo(tsetmc_raw_data=raw["instrumentInfo"])

    async def get_client_type_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/ClientType/GetClientType/{tsetmc_code}/1/0",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_client_type(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> ClientType:
        raw = await self.get_client_type_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return ClientType(tsetmc_raw_data=raw["clientType"])

    async def get_best_limits_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/BestLimits/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_best_limits(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> BestLimits:
        raw = await self.get_best_limits_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return BestLimits(tsetmc_raw_data=raw["bestLimits"])

    async def get_closing_price_daily_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/ClosingPrice/GetClosingPriceDailyList/{tsetmc_code}/0",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_closing_price_daily_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[ClosingPriceDaily]:
        raw = await self.get_closing_price_daily_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [ClosingPriceDaily(tsetmc_raw_data=x) for x in raw["closingPriceDaily"]][::-1]

    async def get_client_type_daily_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/ClientType/GetClientTypeHistory/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_client_type_daily_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[ClientTypeDaily]:
        raw = await self.get_client_type_daily_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [ClientTypeDaily(tsetmc_raw_data=x) for x in raw["clientType"]][::-1]

    async def get_trade_intraday_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Trade/GetTrade/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_trade_intraday_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[TradeIntraday]:
        raw = await self.get_trade_intraday_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [TradeIntraday(tsetmc_raw_data=x) for x in raw["trade"]]

    async def get_price_adjustment_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/ClosingPrice/GetPriceAdjustList/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_price_adjustment_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[PriceAdjustment]:
        raw = await self.get_price_adjustment_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [PriceAdjustment(tsetmc_raw_data=x) for x in raw["priceAdjust"]]

    async def get_instrument_share_change_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentShareChange/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_instrument_share_change(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[InstrumentShareChange]:
        raw = await self.get_instrument_share_change_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [InstrumentShareChange(tsetmc_raw_data=x) for x in raw["instrumentShareChange"]]

    async def get_trade_intraday_hisory_list_raw(
            self,
            tsetmc_code: str,
            date: date,
            detailed: bool = True,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Trade/GetTradeHistory/{tsetmc_code}/\
                {date.year}{date.month:02}{date.day:02}/{not detailed}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_trade_intraday_hisory_list(
            self,
            tsetmc_code: str,
            date: date,
            detailed: bool = True,
            timeout: int = 3
    ) -> list[TradeIntraday]:
        raw = await self.get_trade_intraday_hisory_list_raw(
            tsetmc_code=tsetmc_code,
            date=date,
            detailed=detailed,
            timeout=timeout
        )
        proc = [TradeIntraday(tsetmc_raw_data=x) for x in raw["tradeHistory"]]
        proc.sort(key=lambda x: x.index)
        return proc

    async def get_best_limits_intraday_history_list_raw(
            self,
            tsetmc_code: str,
            date: date,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/BestLimits/{tsetmc_code}/{date.year}{date.month:02}{date.day:02}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_best_limits_intraday_history_list(
            self,
            tsetmc_code: str,
            date: date,
            timeout: int = 3
    ) -> list[BestLimitsHistoryRow]:
        raw = await self.get_best_limits_intraday_history_list_raw(
            tsetmc_code=tsetmc_code,
            date=date,
            timeout=timeout
        )
        return [BestLimitsHistoryRow(tsetmc_raw_data=x) for x in raw["bestLimitsHistory"]]

    async def get_index_history_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Index/GetIndexB2History/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_index_history(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[IndexDaily]:
        raw = await self.get_index_history_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return [IndexDaily(tsetmc_raw_data=x) for x in raw["indexB2"]]

    async def get_instrument_option_info_raw(
            self,
            isin: str,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentOptionByInstrumentID/{isin}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_instrument_option_info(
            self,
            isin: str,
            timeout: int = 3
    ) -> InstrumentOptionInfo:
        raw = await self.get_instrument_option_info_raw(isin=isin, timeout=timeout)
        return InstrumentOptionInfo(tsetmc_raw_data=raw["instrumentOption"])

    async def get_primary_market_overview_raw(
            self,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            "api/MarketData/GetMarketOverview/1",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_primary_market_overview(
            self,
            timeout: int = 3
    ) -> PrimaryMarketOverview:
        raw = await self.get_primary_market_overview_raw(timeout=timeout)
        return PrimaryMarketOverview(tsetmc_raw_data=raw["marketOverview"])

    async def get_secondary_market_overview_raw(
            self,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            "api/MarketData/GetMarketOverview/2",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_secondary_market_overview(
            self,
            timeout: int = 3
    ) -> SecondaryMarketOverview:
        raw = await self.get_secondary_market_overview_raw(timeout=timeout)
        return SecondaryMarketOverview(tsetmc_raw_data=raw["marketOverview"])

    async def get_market_watch_raw(
            self,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            "api/ClosingPrice/GetMarketWatch?market=0&paperTypes[0]=1&paperTypes[1]=2\
                &paperTypes[2]=3&paperTypes[3]=4&paperTypes[4]=5&paperTypes[5]=6\
                    &paperTypes[6]=7&paperTypes[7]=8&paperTypes[8]=9&showTraded=false\
                        &withBestLimits=true&hEven=0&RefID=0",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_market_watch(
            self,
            timeout: int = 3
    ) -> list[MarketWatchTradeData]:
        raw = await self.get_market_watch_raw(timeout=timeout)
        return [MarketWatchTradeData(tsetmc_raw_data=x) for x in raw["marketwatch"]]

    async def get_client_type_all_raw(
            self,
            timeout: int = 3
    ) -> dict:
        req = await self.__client.get(
            "api/ClientType/GetClientTypeAll",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_client_type_all(
            self,
            timeout: int = 3
    ) -> list[MarketWatchClientTypeData]:
        raw = await self.get_client_type_all_raw(timeout=timeout)
        return [MarketWatchClientTypeData(tsetmc_raw_data=x) for x in raw["clientTypeAllDto"]]


class TseClientScraper():
    """
    This class fetches data from tsetmc client.
    """
    base_address: str = "http://service.tsetmc.com/WebService/TseClient.asmx"

    def __init__(self):
        self.__client = httpx.AsyncClient(headers={
            "Host": "service.tsetmc.com",
            "SOAPAction": "http://tsetmc.com/Instrument",
            "accept": "text/xml",
            "Content-type": "text/xml"
        }, base_url=TseClientScraper.base_address)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__client.aclose()

    async def get_instruments_list_raw(
            self,
            timeout: int = 3
    ) -> str:
        xml_data = """\
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xmlns:xsd="http://www.w3.org/2001/XMLSchema" \
xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <Instrument xmlns="http://tsetmc.com/">
            <UserName>string</UserName>
            <Password>string</Password>
            <Flow>unsignedByte</Flow>
        </Instrument>
    </soap:Body>
</soap:Envelope>
"""
        http_content = xml_data.encode(encoding='UTF-8')
        req = await self.__client.post(
            self.base_address,
            content=http_content,
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeError(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return req.text

    async def get_instruments_list(
            self,
            timeout: int = 3
    ) -> list[TseClientInstrumentIdentity]:
        raw = await self.get_instruments_list_raw(timeout=timeout)
        element = BeautifulSoup(raw, features="xml").findChild(
            "InstrumentResult").text
        processed = [TseClientInstrumentIdentity(
            x.split(",")) for x in element.split(";")]
        return [
            x
            for x in processed
            if not x.is_index
        ], [
            x
            for x in processed
            if x.is_index
        ]
