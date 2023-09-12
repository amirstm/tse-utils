import unittest, sys, asyncio
sys.path.append("..")
from TseUtils.tsetmc import TsetmcScraper
from TseUtils.models import instrument

class TestTSETMC(unittest.IsolatedAsyncioTestCase):

    def __init__(self, *args, **kwargs):
        self.sample_instrument = instrument.Instrument(
            instrument.InstrumentIdentification(isin="IRO1FOLD0001", tsetmc_code="46348559193224090", 
                                                ticker="فولاد"))
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
            self.assertTrue(data.total_share_count == 800000000000)

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

if __name__ == '__main__':
    unittest.main()