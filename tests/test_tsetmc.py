import unittest, sys, asyncio
sys.path.append("..")
from tse_utils.tsetmc import TsetmcScraper
from tse_utils.models import instrument
from datetime import datetime, date, time

class TestTSETMC(unittest.IsolatedAsyncioTestCase):

    def __init__(self, *args, **kwargs):
        self.sample_instrument = instrument.Instrument(
            instrument.InstrumentIdentification(isin="IRO1FOLD0001", tsetmc_code="46348559193224090", 
                                                ticker="فولاد"))
        self.sample_date = date(year=2023, month=4, day=30)
        self.sample_index_identification = instrument.IndexIdentification(persian_name="شاخص کل", tsetmc_code="32097828799138957")
        super().__init__(*args, **kwargs)

    async def test_get_instrument_identity_raw(self):
        async with TsetmcScraper() as tsetmc:
            identity = await tsetmc.get_instrument_identity_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertEqual(identity["instrumentIdentity"]["instrumentID"], self.sample_instrument.identification.isin)

    async def test_get_instrument_identity(self):
        async with TsetmcScraper() as tsetmc:
            identity = await tsetmc.get_instrument_identity(self.sample_instrument.identification.tsetmc_code)
            self.assertEqual(identity.isin, self.sample_instrument.identification.isin)

    async def test_get_instrument_search_raw(self):
        async with TsetmcScraper() as tsetmc:
            search_result = await tsetmc.get_instrument_search_raw(self.sample_instrument.identification.ticker)
            self.assertTrue(any(x["insCode"] == self.sample_instrument.identification.tsetmc_code for x in search_result["instrumentSearch"]))

    async def test_get_instrument_search(self):
        async with TsetmcScraper() as tsetmc:
            search_result = await tsetmc.get_instrument_search(self.sample_instrument.identification.ticker)
            self.assertTrue(any([x.tsetmc_code == self.sample_instrument.identification.tsetmc_code for x in search_result]))

    async def test_get_closing_price_info_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_closing_price_info_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("closingPriceInfo" in data)

    async def test_get_closing_price_info(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_closing_price_info(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(not data.last_trade_datetime is None)
            self.assertTrue(data.min_price * data.trade_volume <= data.trade_value)

    async def test_get_instrument_info_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_instrument_info_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(data["instrumentInfo"]["instrumentID"] == self.sample_instrument.identification.isin)

    async def test_get_instrument_info(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_instrument_info(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(data.isin == self.sample_instrument.identification.isin)
            self.assertTrue(data.total_shares == 800000000000)

    async def test_get_client_type_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_client_type_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("buy_CountN" in data["clientType"])

    async def test_get_client_type(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_client_type(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(data.legal_sell_volume + data.natural_sell_volume == data.legal_buy_volume + data.natural_buy_volume)

    async def test_get_best_limits_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_best_limits_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("bestLimits" in data)

    async def test_get_best_limits(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_best_limits(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(len(data.rows) == 5)

    async def test_get_closing_price_daily_list_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_closing_price_daily_list_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("closingPriceDaily" in data)

    async def test_get_closing_price_daily_list(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_closing_price_daily_list(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(len(data) > 1000)
            chosen_date = datetime(year=2023, month=9, day=11)
            date_data = next(x for x in data if x.last_trade_datetime.date() == chosen_date.date())
            self.assertTrue(date_data.trade_volume == 74309985)

    async def test_get_client_type_history_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_client_type_daily_list_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("clientType" in data)

    async def test_get_client_type_history(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_client_type_daily_list(self.sample_instrument.identification.tsetmc_code)
            chosen_date = date(year=2023, month=9, day=11)
            date_data = next(x for x in data if x.record_date == chosen_date)
            self.assertTrue(date_data.legal_buy_num == 13)
            self.assertTrue(date_data.legal_buy_value == 259393764720)
            self.assertTrue(date_data.legal_buy_volume == 46754064)
            self.assertTrue(date_data.legal_sell_num == 15)
            self.assertTrue(date_data.legal_sell_value == 192455986390)
            self.assertTrue(date_data.legal_sell_volume == 34727215)
            self.assertTrue(date_data.natural_buy_num == 1277)
            self.assertTrue(date_data.natural_buy_value == 152695292260)
            self.assertTrue(date_data.natural_buy_volume == 27555921)
            self.assertTrue(date_data.natural_sell_num == 1242)
            self.assertTrue(date_data.natural_sell_value == 219633070590)
            self.assertTrue(date_data.natural_sell_volume == 39582770)

    async def test_get_trade_intraday_list_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_trade_intraday_list_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("trade" in data)

    async def test_get_trade_intraday_list(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_trade_intraday_list(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(len(data) != 0)

    async def test_get_price_adjustment_list_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_price_adjustment_list_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("priceAdjust" in data)

    async def test_get_price_adjustment_list(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_price_adjustment_list(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(len(data) > 10)
            self.assertTrue(any(x.record_date == date(year=2023, month=7, day=22) 
                                and x.price_before == 5460 
                                and x.price_after == 4960 for x in data))

    async def test_get_instrument_share_change_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_instrument_share_change_raw(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue("instrumentShareChange" in data)

    async def test_get_instrument_share_change(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_instrument_share_change(self.sample_instrument.identification.tsetmc_code)
            self.assertTrue(len(data) > 5)
            self.assertTrue(any(x.record_date == date(year=2022, month=8, day=9) 
                                and x.total_shares_before == 293000000000 
                                and x.total_shares_after == 530000000000 for x in data))

    async def test_get_trade_intraday_hisory_list_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_trade_intraday_hisory_list_raw(
                self.sample_instrument.identification.tsetmc_code, self.sample_date)
            self.assertTrue("tradeHistory" in data)

    async def test_get_trade_intraday_hisory_list(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_trade_intraday_hisory_list(
                self.sample_instrument.identification.tsetmc_code, self.sample_date)
            chosen_data = next(x for x in data if x.index == 15552)
            self.assertTrue(chosen_data.volume == 100790 
                            and chosen_data.price == 7250 
                            and chosen_data.record_time == time(hour=12, minute=26, second=6)
                            and chosen_data.is_canceled)

    async def test_get_best_limits_intraday_history_list_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_best_limits_intraday_history_list_raw(
                self.sample_instrument.identification.tsetmc_code, self.sample_date)
            self.assertTrue("bestLimitsHistory" in data)

    async def test_get_best_limits_intraday_history_list(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_best_limits_intraday_history_list(
                self.sample_instrument.identification.tsetmc_code, self.sample_date)
            self.assertTrue(any(x.record_time == time(hour=8, minute=45, second=36) and
                                x.row_number == 5 and x.reference_id == 11679170214 and
                                x.demand_volume == 163213 and x.demand_price == 7000 for x in data))

    async def test_get_index_history_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_index_history_raw(self.sample_index_identification.tsetmc_code)
            self.assertTrue("indexB2" in data)

    async def test_get_index_history(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_index_history(self.sample_index_identification.tsetmc_code)
            self.assertTrue(any(x.record_date == date(year=2023, month=9, day=13) and
                                x.last_value == 2126741.7 and x.min_value == 2126690 and
                                x.max_value == 2130510 for x in data))

if __name__ == '__main__':
    unittest.main()