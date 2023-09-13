import asyncio, httpx, json
from tse_utils.exceptions import MyProjectError
from tse_utils.models.enums import *
from dataclasses import dataclass
from datetime import datetime, date, time

@dataclass
class InstrumentIdentity:
    isin: str = None
    tsetmc_code: str = None
    ticker: str = None
    name_persian: str = None
    name_english: str = None
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
        self.sector_code = int(tsetmc_raw_data["sector"]["cSecVal"].replace(" ", ""))
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
class ClosingPriceInfo:
    last_trade_datetime: datetime = None
    close_price: int = None
    last_price: int = None
    open_price: int = None
    max_price: int = None
    min_price: int = None
    previous_price: int = None
    trade_num: int = None
    trade_value: int = None
    trade_volume: int = None
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
        self.nsc = Nsc[str(tsetmc_raw_data["instrumentState"]["cEtaval"]).replace(" ", "")]
        ltd_date = tsetmc_raw_data["finalLastDate"]
        ltd_time = tsetmc_raw_data["hEven"]
        self.last_trade_datetime = datetime(year=ltd_date // 10000, month=ltd_date // 100 % 100, day=ltd_date % 100,
                                            hour=ltd_time // 10000, minute=ltd_time // 100 % 100, second=ltd_time % 100)

@dataclass
class InstrumentInfo:
    isin: str = None
    name_persian: str = None
    name_english: str = None
    ticker: str = None
    base_volume: int = None
    liquid_percentage: float = None
    max_price_weekly: int = None
    min_price_weekly: int = None
    max_price_annual: int = None
    min_price_annual: int = None
    average_trade_volume_monthly: int = None
    total_shares: int = None
    market_code: int = None
    market_title: str = None
    max_price_threshold: int = None
    min_price_threshold: int = None
    type_id: int = None

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
        self.liquid_percentage = None if len(tsetmc_raw_data["kAjCapValCpsIdx"]) == 0 else float(tsetmc_raw_data["kAjCapValCpsIdx"])

@dataclass
class ClientType:
    legal_buy_num: int = None
    legal_buy_volume: int = None
    legal_sell_num: int = None
    legal_sell_volume: int = None
    natural_buy_num: int = None
    natural_buy_volume: int = None
    natural_sell_num: int = None
    natural_sell_volume: int = None

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
class BestLimitsRow:
    demand_num: int = None
    demand_volume: int = None
    demand_price: int = None
    supply_num: int = None
    supply_volume: int = None
    supply_price: int = None

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
        self.last_trade_datetime = datetime(year=ltd_date // 10000, month=ltd_date // 100 % 100, day=ltd_date % 100,
                                            hour=ltd_time // 10000, minute=ltd_time // 100 % 100, second=ltd_time % 100)

@dataclass
class ClientTypeDaily(ClientType):
    legal_buy_value: int = None
    legal_sell_value: int = None
    natural_buy_value: int = None
    natural_sell_value: int = None
    record_date: date = None

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
        self.record_date = date(year=rd_date // 10000, month=rd_date // 100 % 100, day=rd_date % 100)

@dataclass
class TradeIntraday():
    price: int = None
    volume: int = None
    index: int = None
    record_time: time = None
    is_canceled: bool = None

    def __init__(self, tsetmc_raw_data):
        self.price = tsetmc_raw_data["pTran"]
        self.volume = tsetmc_raw_data["qTitTran"]
        self.index = tsetmc_raw_data["nTran"]
        hEven = tsetmc_raw_data["hEven"]
        self.record_time = time(hour=hEven // 10000, minute=hEven // 100 % 100, second=hEven % 100)
        self.is_canceled = bool(tsetmc_raw_data["canceled"])

@dataclass
class PriceAdjustment:
    record_date: date = None
    price_before: int = None
    price_after: int = None

    def __init__(self, tsetmc_raw_data):
        self.price_before = tsetmc_raw_data["pClosingNotAdjusted"]
        self.price_after = tsetmc_raw_data["pClosing"]
        dEven = tsetmc_raw_data["dEven"]
        self.record_date = date(year=dEven // 10000, month = dEven // 100 % 100, day=dEven % 100)

@dataclass
class InstrumentShareChange:
    record_date: date = None
    total_shares_before: int = None
    total_shares_after: int = None

    def __init__(self, tsetmc_raw_data):
        self.total_shares_before = tsetmc_raw_data["numberOfShareOld"]
        self.total_shares_after = tsetmc_raw_data["numberOfShareNew"]
        dEven = tsetmc_raw_data["dEven"]
        self.record_date = date(year=dEven // 10000, month = dEven // 100 % 100, day=dEven % 100)

class TsetmcScrapeError(MyProjectError):
   """Tsetmc bad response status error."""
   def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.status_code = kwargs.get('status_code')
        
class TsetmcScraper():
    """
    This class fetches data from tsetmc.com, the official website for Tehran Stock Exchange market data.
    """
    def __init__(self, tsetmc_domain: str = "cdn.tsetmc.com"):
        self.tsetmc_domain = tsetmc_domain
        self.__client = httpx.AsyncClient(headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "accept": "application/json, text/plain, */*"
        }, base_url=f"http://{tsetmc_domain}/")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.__client.aclose()

    async def get_instrument_identity_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/Instrument/GetInstrumentIdentity/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)

    async def get_instrument_identity(self, tsetmc_code: str, timeout: int = 3) -> InstrumentIdentity:
        raw = await self.get_instrument_identity_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return InstrumentIdentity(tsetmc_raw_data=raw["instrumentIdentity"])

    async def get_instrument_search_raw(self, search_value: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/Instrument/GetInstrumentSearch/{search_value}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)

    async def get_instrument_search(self, search_value: str, timeout: int = 3) -> list[InstrumentSearchItem]:
        raw = await self.get_instrument_search_raw(search_value=search_value, timeout=timeout)
        return [InstrumentSearchItem(x) for x in raw["instrumentSearch"]]

    async def get_closing_price_info_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/ClosingPrice/GetClosingPriceInfo/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)
    
    async def get_closing_price_info(self, tsetmc_code: str, timeout: int = 3) -> ClosingPriceInfo:
        raw = await self.get_closing_price_info_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return ClosingPriceInfo(tsetmc_raw_data=raw["closingPriceInfo"])

    async def get_instrument_info_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/Instrument/GetInstrumentInfo/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)
        
    async def get_instrument_info(self, tsetmc_code: str, timeout: int = 3) -> InstrumentInfo:
        raw = await self.get_instrument_info_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return InstrumentInfo(tsetmc_raw_data=raw["instrumentInfo"])

    async def get_client_type_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/ClientType/GetClientType/{tsetmc_code}/1/0", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)
        
    async def get_client_type(self, tsetmc_code: str, timeout: int = 3) -> ClientType:
        raw = await self.get_client_type_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return ClientType(tsetmc_raw_data=raw["clientType"])

    async def get_best_limits_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/BestLimits/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)

    async def get_best_limits(self, tsetmc_code: str, timeout: int = 3) -> BestLimits:
        raw = await self.get_best_limits_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return BestLimits(tsetmc_raw_data=raw["bestLimits"])

    async def get_closing_price_daily_list_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/ClosingPrice/GetClosingPriceDailyList/{tsetmc_code}/0", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)

    async def get_closing_price_daily_list(self, tsetmc_code: str, timeout: int = 3) -> list[ClosingPriceDaily]:
        raw = await self.get_closing_price_daily_list_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return [ClosingPriceDaily(tsetmc_raw_data=x) for x in raw["closingPriceDaily"]][::-1]

    async def get_client_type_daily_list_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/ClientType/GetClientTypeHistory/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)
        
    async def get_client_type_daily_list(self, tsetmc_code: str, timeout: int = 3) -> list[ClientTypeDaily]:
        raw = await self.get_client_type_daily_list_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return [ClientTypeDaily(tsetmc_raw_data=x) for x in raw["clientType"]][::-1]

    async def get_trade_intraday_list_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/Trade/GetTrade/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)
    
    async def get_trade_intraday_list(self, tsetmc_code: str, timeout: int = 3) -> list[TradeIntraday]:
        raw = await self.get_trade_intraday_list_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return [TradeIntraday(tsetmc_raw_data=x) for x in raw["trade"]]

    async def get_price_adjustment_list_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/ClosingPrice/GetPriceAdjustList/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)
        
    async def get_price_adjustment_list(self, tsetmc_code: str, timeout: int = 3) -> list[PriceAdjustment]:
        raw = await self.get_price_adjustment_list_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return [PriceAdjustment(tsetmc_raw_data=x) for x in raw["priceAdjust"]]

    async def get_instrument_share_change_raw(self, tsetmc_code: str, timeout: int = 3) -> dict:
        r = await self.__client.get(f"api/Instrument/GetInstrumentShareChange/{tsetmc_code}", timeout=timeout)
        if r.status_code != 200:
            raise TsetmcScrapeError(f"Bad response: [{r.status_code}]", status_code=r.status_code)
        return json.loads(r.text)
        
    async def get_instrument_share_change(self, tsetmc_code: str, timeout: int = 3) -> list[InstrumentShareChange]:
        raw = await self.get_instrument_share_change_raw(tsetmc_code=tsetmc_code, timeout=timeout)
        return [InstrumentShareChange(tsetmc_raw_data=x) for x in raw["instrumentShareChange"]]
