import unittest, sys, asyncio
sys.path.append("..")
from TseUtils.tsetmc import TsetmcScraper
from TseUtils.models import instrument

class TestTSETMC(unittest.IsolatedAsyncioTestCase):

    def __init__(self, *args, **kwargs):
        self.test_instrument = instrument.Instrument(
            instrument.InstrumentIdentification(isin="IRO1FOLD0001", tsetmc_code="46348559193224090", 
                                                ticker="فولاد"))
        super().__init__(*args, **kwargs)

    async def test_get_instrument_identity_raw(self):
        async with TsetmcScraper() as tsetmc:
            identity = await tsetmc.get_instrument_identity_raw(self.test_instrument.identification.tsetmc_code)
            self.assertEqual(identity["instrumentIdentity"]["instrumentID"], self.test_instrument.identification.isin)

    async def test_get_instrument_identity(self):
        async with TsetmcScraper() as tsetmc:
            identity = await tsetmc.get_instrument_identity(self.test_instrument.identification.tsetmc_code)
            self.assertEqual(identity.isin, self.test_instrument.identification.isin)

    async def test_get_instrument_search_raw(self):
        async with TsetmcScraper() as tsetmc:
            search_result = await tsetmc.get_instrument_search_raw(self.test_instrument.identification.ticker)
            self.assertTrue(any(x["insCode"] == self.test_instrument.identification.tsetmc_code for x in search_result["instrumentSearch"]))

    async def test_get_instrument_search(self):
        async with TsetmcScraper() as tsetmc:
            search_result = await tsetmc.get_instrument_search(self.test_instrument.identification.ticker)
            self.assertTrue(any([x.tsetmc_code == self.test_instrument.identification.tsetmc_code for x in search_result]))

    async def test_get_closing_price_info_raw(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_closing_price_info_raw(self.test_instrument.identification.tsetmc_code)
            self.assertTrue("closingPriceInfo" in data)

    async def test_get_closing_price_info(self):
        async with TsetmcScraper() as tsetmc:
            data = await tsetmc.get_closing_price_info(self.test_instrument.identification.tsetmc_code)
            self.assertTrue(not data.last_trade_datetime is None)
            self.assertTrue(data.min_price * data.trade_volume <= data.trade_value)

if __name__ == '__main__':
    unittest.main()