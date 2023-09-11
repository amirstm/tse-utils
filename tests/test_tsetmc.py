import unittest, sys, asyncio
sys.path.append("..")
from TseUtils.tsetmc import TsetmcScraper

# asyncio.run(get_instrument_identity())
class TestSum(unittest.IsolatedAsyncioTestCase):

    async def test_get_instrument_identity_raw(self):
        async with TsetmcScraper() as tsetmc:
            identity = await tsetmc.get_instrument_identity_raw("46348559193224090")
            self.assertEqual(identity["instrumentIdentity"]["instrumentID"], "IRO1FOLD0001")

    async def test_get_instrument_identity(self):
        async with TsetmcScraper() as tsetmc:
            identity = await tsetmc.get_instrument_identity("46348559193224090")
            self.assertEqual(identity.isin, "IRO1FOLD0001")

if __name__ == '__main__':
    unittest.main()