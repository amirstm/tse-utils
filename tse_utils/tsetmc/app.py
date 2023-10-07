"""
This module uses httpx to fetch data asynchronously \
from the TSETMC website. 
"""
from datetime import date
import json
import httpx
from bs4 import BeautifulSoup
from tse_utils.tsetmc.models import (
    TsetmcScrapeException,
    InstrumentIdentification,
    InstrumentSearchItem,
    ClosingPriceInfo,
    InstrumentInfo,
    ClientType,
    BestLimits,
    ClosingPriceDaily,
    ClientTypeDaily,
    TradeIntraday,
    PriceAdjustment,
    InstrumentShareChange,
    BestLimitsHistoryRow,
    IndexDaily,
    PrimaryMarketOverview,
    InstrumentOptionInfo,
    SecondaryMarketOverview,
    MarketWatchTradeData,
    MarketWatchClientTypeData
)


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
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_instrument_identity(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> InstrumentIdentification:
        raw = await self.get_instrument_identity_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return InstrumentIdentification(
            tsetmc_code=tsetmc_code,
            tsetmc_raw_data=raw["instrumentIdentity"]
        )

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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
        return InstrumentInfo(
            tsetmc_code=tsetmc_code,
            tsetmc_raw_data=raw["instrumentInfo"]
        )

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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
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
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]", status_code=req.status_code)
        return json.loads(req.text)

    async def get_client_type_all(
            self,
            timeout: int = 3
    ) -> list[MarketWatchClientTypeData]:
        raw = await self.get_client_type_all_raw(timeout=timeout)
        return [MarketWatchClientTypeData(tsetmc_raw_data=x) for x in raw["clientTypeAllDto"]]
