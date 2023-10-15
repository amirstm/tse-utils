"""Test tsetmc and tse_client modules in tse_utils library"""
import unittest
from datetime import datetime, date, time
from time import sleep
import httpx
from tse_utils.tsetmc import TsetmcScraper
from tse_utils.tse_client import TseClientScraper
from tse_utils.models import instrument


class TestTSETMC(unittest.IsolatedAsyncioTestCase):
    """Test tsetmc and tse_client modules in tse_utils library"""
    retries_on_timeout = 5

    def __init__(self, *args, **kwargs):
        self.sample_instrument = instrument.Instrument(
            instrument.InstrumentIdentification(
                isin="IRO1FOLD0001", tsetmc_code="46348559193224090",
                ticker="فولاد"
            ))
        self.sample_date = date(year=2023, month=4, day=30)
        self.sample_index_identification = instrument.IndexIdentification(
            persian_name="شاخص کل", tsetmc_code="32097828799138957")
        self.sample_option = instrument.OptionInstrument(
            exercise_date=date(year=2023, month=10, day=18),
            exercise_price=1653,
            underlying=self.sample_instrument,
            identification=instrument.InstrumentIdentification(
                isin="IRO9FOLD6821",
                ticker="ضفلا7020",
                tsetmc_code="37762443198265540"
            )
        )
        super().__init__(*args, **kwargs)

    async def test_get_instrument_identity(self):
        """Test instrument identity fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    identity = await tsetmc.get_instrument_identity(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertEqual(
                        identity.isin, self.sample_instrument.identification.isin)
            except httpx.ConnectTimeout as exc:
                if trial_ind == self.retries_on_timeout - 1:
                    raise exc
                sleep(1)

    async def test_get_instrument_search(self):
        """Test instrument search on TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    search_result = await tsetmc.get_instrument_search(
                        self.sample_instrument.identification.ticker
                    )
                    self.assertTrue(any(
                        x.tsetmc_code == self.sample_instrument.identification.tsetmc_code
                        for x in search_result
                    ))
            except httpx.ConnectTimeout as exc:
                if trial_ind == self.retries_on_timeout - 1:
                    raise exc
                sleep(1)

    async def test_get_closing_price_info(self):
        """Test instrument current trade data fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_closing_price_info(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(not data.last_trade_datetime is None)
                    self.assertTrue(data.min_price *
                                    data.trade_volume <= data.trade_value)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_instrument_info(self):
        """Test instrument home page data fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_instrument_info(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(
                        data.isin == self.sample_instrument.identification.isin)
                    self.assertTrue(data.total_shares == 800000000000)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_client_type(self):
        """Test instrument current client type fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_client_type(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(
                        data.legal.sell.volume + data.natural.sell.volume ==
                        data.legal.buy.volume + data.natural.buy.volume
                    )
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_best_limits(self):
        """Test instrument current order book fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_best_limits(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(len(data.rows) == 5)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_closing_price_daily_list(self):
        """Test instrument historical daily prices fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_closing_price_daily_list(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(len(data) > 1000)
                    chosen_date = datetime(year=2023, month=9, day=11)
                    date_data = next(
                        x for x in data if x.last_trade_datetime.date() == chosen_date.date())
                    self.assertTrue(date_data.trade_volume == 74309985)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_client_type_history(self):
        """Test instrument historical daily client type fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_client_type_daily_list(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    chosen_date = date(year=2023, month=9, day=11)
                    date_data = next(
                        x for x in data if x.record_date == chosen_date)
                    self.assertTrue(date_data.legal.buy.num == 13)
                    self.assertTrue(date_data.legal.buy.value == 259393764720)
                    self.assertTrue(date_data.legal.buy.volume == 46754064)
                    self.assertTrue(date_data.legal.sell.num == 15)
                    self.assertTrue(date_data.legal.sell.value == 192455986390)
                    self.assertTrue(date_data.legal.sell.volume == 34727215)
                    self.assertTrue(date_data.natural.buy.num == 1277)
                    self.assertTrue(
                        date_data.natural.buy.value == 152695292260)
                    self.assertTrue(date_data.natural.buy.volume == 27555921)
                    self.assertTrue(date_data.natural.sell.num == 1242)
                    self.assertTrue(
                        date_data.natural.sell.value == 219633070590)
                    self.assertTrue(date_data.natural.sell.volume == 39582770)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_trade_intraday_list(self):
        """Test instrument intradary microtrades fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_trade_intraday_list(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(len(data) != 0)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_price_adjustment_list(self):
        """Test instrument historical price adjustments fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_price_adjustment_list(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(len(data) > 10)
                    self.assertTrue(any(x.date == date(year=2023, month=7, day=22)
                                        and x.price_before == 5460
                                        and x.price_after == 4960 for x in data))
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_instrument_share_change(self):
        """Test instrument historical equity change fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_instrument_share_change(
                        self.sample_instrument.identification.tsetmc_code
                    )
                    self.assertTrue(len(data) > 5)
                    self.assertTrue(any(
                        x.record_date == date(year=2022, month=8, day=9)
                        and x.total_shares_before == 293000000000
                        and x.total_shares_after == 530000000000
                        for x in data
                    ))
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_trade_intraday_hisory_list(self):
        """Test instrument historical intraday microtrades fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_trade_intraday_hisory_list(
                        self.sample_instrument.identification.tsetmc_code, self.sample_date)
                    chosen_data = next(x for x in data if x.index == 15552)
                    self.assertTrue(chosen_data.volume == 100790
                                    and chosen_data.price == 7250
                                    and chosen_data.time == time(hour=12, minute=26, second=6)
                                    and chosen_data.is_canceled)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_best_limits_intraday_history_list(self):
        """Test instrument historical orderbook fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_best_limits_intraday_history_list(
                        self.sample_instrument.identification.tsetmc_code, self.sample_date
                    )
                    self.assertTrue(
                        any(x.record_time == time(hour=8, minute=45, second=36) and
                            x.row_number == 5 and x.reference_id == 11679170214 and
                            x.demand.volume == 163213 and x.demand.price == 7000
                            for x in data
                            )
                    )
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_index_history(self):
        """Test historical index data fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_index_history(
                        self.sample_index_identification.tsetmc_code
                    )
                    self.assertTrue(
                        any(
                            x.record_date == date(year=2023, month=9, day=13) and
                            x.close_value == 2126741.7 and x.min_value == 2126690 and
                            x.max_value == 2130510
                            for x in data
                        )
                    )
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_instrument_option_info(self):
        """Test instrument option info fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_instrument_option_info(
                        self.sample_option.identification.isin
                    )
                    self.assertTrue(
                        data.exercise_date ==
                        self.sample_option.exercise_date and
                        data.exercise_price ==
                        self.sample_option.exercise_price and
                        data.underlying_tsetmc_code ==
                        self.sample_instrument.identification.tsetmc_code
                    )
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_primary_market_overview(self):
        """Test primary market overview fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_primary_market_overview()
                    self.assertTrue(data.market_value > 4e16)
                    self.assertTrue(data.overall_index.close_value > 1e6)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_secondary_market_overview(self):
        """Test secondary market overview fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_secondary_market_overview()
                    self.assertTrue(data.market_value > 1e16)
                    self.assertTrue(
                        data.secondary_market_index.close_value > 1e4)
                    self.assertTrue(data.tertiary_market_value > 1e15)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_market_watch(self):
        """Test market watch fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_market_watch()
                    self.assertTrue(len(data) > 100)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_get_client_type_all(self):
        """Test market client type fetch from TSETMC"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TsetmcScraper() as tsetmc:
                    data = await tsetmc.get_client_type_all()
                    self.assertTrue(len(data) > 100)
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)

    async def test_tse_client_get_instruments_list(self):
        """Test fetch instruments list from TseClient"""
        for trial_ind in range(self.retries_on_timeout):
            try:
                async with TseClientScraper() as tse_client:
                    instruments, _ = await tse_client.get_instruments_list()
                    self.assertTrue(len(instruments) > 0)
                    self.assertTrue(
                        any(
                            x.tsetmc_code == self.sample_instrument.identification.tsetmc_code and
                            x.isin == self.sample_instrument.identification.isin
                            for x in instruments
                        )
                    )
            except httpx.ConnectTimeout:
                if trial_ind == self.retries_on_timeout - 1:
                    raise
                sleep(1)


if __name__ == '__main__':
    unittest.main()
