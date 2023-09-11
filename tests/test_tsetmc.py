import unittest, sys, asyncio
sys.path.append("..")
from TseUtils.tsetmc import TsetmcScraper

# asyncio.run(get_instrument_identity())
class TestSum(unittest.IsolatedAsyncioTestCase):

    async def test_get_instrument_identity(self):
        tsetmc = TsetmcScraper()
        identity = await tsetmc.get_instrument_identity("46348559193224090")
        self.assertTrue(identity["instrumentIdentity"]["instrumentID"] == "IRO1FOLD0001")

if __name__ == '__main__':
    unittest.main()