"""
This module uses httpx to fetch data asynchronously \
from the TSETMC website. 
"""
from datetime import date
import json
import httpx
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

    async def __get_instrument_identity_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument identity card"""
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentIdentity/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_instrument_identity(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> InstrumentIdentification:
        """Get processed instrument identity card"""
        raw = await self.__get_instrument_identity_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return InstrumentIdentification(
            tsetmc_code=tsetmc_code,
            tsetmc_raw_data=raw["instrumentIdentity"]
        )

    async def __get_instrument_search_raw(
            self,
            search_value: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument search results"""
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentSearch/{search_value}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_instrument_search(
            self,
            search_value: str,
            timeout: int = 3
    ) -> list[InstrumentSearchItem]:
        """Get and process instrument search results"""
        raw = await self.__get_instrument_search_raw(
            search_value=search_value,
            timeout=timeout
        )
        return [InstrumentSearchItem(x) for x in raw["instrumentSearch"]]

    async def __get_closing_price_info_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument current trade data"""
        req = await self.__client.get(
            f"api/ClosingPrice/GetClosingPriceInfo/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_closing_price_info(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> ClosingPriceInfo:
        """Get and process instrument current trade data"""
        raw = await self.__get_closing_price_info_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return ClosingPriceInfo(tsetmc_raw_data=raw["closingPriceInfo"])

    async def __get_instrument_info_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument home page data"""
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentInfo/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_instrument_info(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> InstrumentInfo:
        """Get and process instrument home page data"""
        raw = await self.__get_instrument_info_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return InstrumentInfo(
            tsetmc_code=tsetmc_code,
            tsetmc_raw_data=raw["instrumentInfo"]
        )

    async def __get_client_type_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument current client type data"""
        req = await self.__client.get(
            f"api/ClientType/GetClientType/{tsetmc_code}/1/0",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_client_type(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> ClientType:
        """Get and process instrument current client type data"""
        raw = await self.__get_client_type_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return ClientType(tsetmc_raw_data=raw["clientType"])

    async def __get_best_limits_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument order book data"""
        req = await self.__client.get(
            f"api/BestLimits/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_best_limits(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> BestLimits:
        """Get and process instrument order book data"""
        raw = await self.__get_best_limits_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return BestLimits(tsetmc_raw_data=raw["bestLimits"])

    async def __get_closing_price_daily_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument daily historical trade data"""
        req = await self.__client.get(
            f"api/ClosingPrice/GetClosingPriceDailyList/{tsetmc_code}/0",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_closing_price_daily_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[ClosingPriceDaily]:
        """Get and process instrument daily historical trade data"""
        raw = await self.__get_closing_price_daily_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [
            ClosingPriceDaily(tsetmc_raw_data=x)
            for x in raw["closingPriceDaily"]
        ][::-1]

    async def __get_client_type_daily_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument daily historical client type data"""
        req = await self.__client.get(
            f"api/ClientType/GetClientTypeHistory/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_client_type_daily_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[ClientTypeDaily]:
        """Get and process instrument daily historical client type data"""
        raw = await self.__get_client_type_daily_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [
            ClientTypeDaily(tsetmc_raw_data=x)
            for x in raw["clientType"]
        ][::-1]

    async def __get_trade_intraday_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument intraday microtrades data"""
        req = await self.__client.get(
            f"api/Trade/GetTrade/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_trade_intraday_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[TradeIntraday]:
        """Get and process instrument intraday microtrades data"""
        raw = await self.__get_trade_intraday_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [TradeIntraday(tsetmc_raw_data=x) for x in raw["trade"]]

    async def __get_price_adjustment_list_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument historical price adjustments"""
        req = await self.__client.get(
            f"api/ClosingPrice/GetPriceAdjustList/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_price_adjustment_list(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[PriceAdjustment]:
        """Get and process instrument historical price adjustments"""
        raw = await self.__get_price_adjustment_list_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [PriceAdjustment(tsetmc_raw_data=x) for x in raw["priceAdjust"]]

    async def __get_instrument_share_change_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument historical share changes"""
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentShareChange/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_instrument_share_change(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[InstrumentShareChange]:
        """Get and process instrument historical share changes"""
        raw = await self.__get_instrument_share_change_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [
            InstrumentShareChange(tsetmc_raw_data=x)
            for x in raw["instrumentShareChange"]
        ]

    async def __get_trade_intraday_hisory_list_raw(
            self,
            tsetmc_code: str,
            query_date: date,
            detailed: bool = True,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument historical intraday microtrades"""
        req = await self.__client.get(
            f"api/Trade/GetTradeHistory/{tsetmc_code}/\
                {query_date.year}{query_date.month:02}{query_date.day:02}/\
                    {not detailed}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_trade_intraday_hisory_list(
            self,
            tsetmc_code: str,
            query_date: date,
            detailed: bool = True,
            timeout: int = 3
    ) -> list[TradeIntraday]:
        """Get and process instrument historical intraday microtrades"""
        raw = await self.__get_trade_intraday_hisory_list_raw(
            tsetmc_code=tsetmc_code,
            query_date=query_date,
            detailed=detailed,
            timeout=timeout
        )
        proc = [
            TradeIntraday(tsetmc_raw_data=x)
            for x in raw["tradeHistory"]
        ]
        proc.sort(key=lambda x: x.index)
        return proc

    async def __get_best_limits_intraday_history_list_raw(
            self,
            tsetmc_code: str,
            query_date: date,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument historical intraday order book"""
        req = await self.__client.get(
            f"api/BestLimits/{tsetmc_code}/{query_date.year}\
{query_date.month:02}{query_date.day:02}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_best_limits_intraday_history_list(
            self,
            tsetmc_code: str,
            query_date: date,
            timeout: int = 3
    ) -> list[BestLimitsHistoryRow]:
        """Get and process instrument historical intraday order book"""
        raw = await self.__get_best_limits_intraday_history_list_raw(
            tsetmc_code=tsetmc_code,
            query_date=query_date,
            timeout=timeout
        )
        return [
            BestLimitsHistoryRow(tsetmc_raw_data=x)
            for x in raw["bestLimitsHistory"]
        ]

    async def __get_index_history_raw(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> dict:
        """Get raw index history"""
        req = await self.__client.get(
            f"api/Index/GetIndexB2History/{tsetmc_code}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_index_history(
            self,
            tsetmc_code: str,
            timeout: int = 3
    ) -> list[IndexDaily]:
        """Get and process index history"""
        raw = await self.__get_index_history_raw(
            tsetmc_code=tsetmc_code,
            timeout=timeout
        )
        return [IndexDaily(tsetmc_raw_data=x) for x in raw["indexB2"]]

    async def __get_instrument_option_info_raw(
            self,
            isin: str,
            timeout: int = 3
    ) -> dict:
        """Get raw instrument option info"""
        req = await self.__client.get(
            f"api/Instrument/GetInstrumentOptionByInstrumentID/{isin}",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_instrument_option_info(
            self,
            isin: str,
            timeout: int = 3
    ) -> InstrumentOptionInfo:
        """Get and process instrument option info"""
        raw = await self.__get_instrument_option_info_raw(
            isin=isin,
            timeout=timeout
        )
        return InstrumentOptionInfo(tsetmc_raw_data=raw["instrumentOption"])

    async def __get_primary_market_overview_raw(
            self,
            timeout: int = 3
    ) -> dict:
        """Get raw primary market overview"""
        req = await self.__client.get(
            "api/MarketData/GetMarketOverview/1",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_primary_market_overview(
            self,
            timeout: int = 3
    ) -> PrimaryMarketOverview:
        """Get and process primary market overview"""
        raw = await self.__get_primary_market_overview_raw(
            timeout=timeout
        )
        return PrimaryMarketOverview(
            tsetmc_raw_data=raw["marketOverview"]
        )

    async def __get_secondary_market_overview_raw(
            self,
            timeout: int = 3
    ) -> dict:
        """Get raw secondary market overview"""
        req = await self.__client.get(
            "api/MarketData/GetMarketOverview/2",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_secondary_market_overview(
            self,
            timeout: int = 3
    ) -> SecondaryMarketOverview:
        """Get and process secondary market overview"""
        raw = await self.__get_secondary_market_overview_raw(
            timeout=timeout
        )
        return SecondaryMarketOverview(
            tsetmc_raw_data=raw["marketOverview"]
        )

    async def __get_market_watch_raw(
            self,
            timeout: int = 3
    ) -> dict:
        """Get raw market watch page"""
        req = await self.__client.get(
            "api/ClosingPrice/GetMarketWatch?market=0&paperTypes[0]=1&paperTypes[1]=2\
                &paperTypes[2]=3&paperTypes[3]=4&paperTypes[4]=5&paperTypes[5]=6\
                    &paperTypes[6]=7&paperTypes[7]=8&paperTypes[8]=9&showTraded=false\
                        &withBestLimits=true&hEven=0&RefID=0",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_market_watch(
            self,
            timeout: int = 3
    ) -> list[MarketWatchTradeData]:
        """Get and process market watch page"""
        raw = await self.__get_market_watch_raw(
            timeout=timeout
        )
        return [
            MarketWatchTradeData(tsetmc_raw_data=x)
            for x in raw["marketwatch"]
        ]

    async def __get_client_type_all_raw(
            self,
            timeout: int = 3
    ) -> dict:
        """Get raw market client type"""
        req = await self.__client.get(
            "api/ClientType/GetClientTypeAll",
            timeout=timeout
        )
        if req.status_code != 200:
            raise TsetmcScrapeException(
                f"Bad response: [{req.status_code}]",
                status_code=req.status_code
            )
        return json.loads(req.text)

    async def get_client_type_all(
            self,
            timeout: int = 3
    ) -> list[MarketWatchClientTypeData]:
        """Get and process market client type"""
        raw = await self.__get_client_type_all_raw(
            timeout=timeout
        )
        return [
            MarketWatchClientTypeData(tsetmc_raw_data=x)
            for x in raw["clientTypeAllDto"]
        ]
