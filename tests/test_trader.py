import unittest, sys, asyncio
sys.path.append("..")
from tse_utils.models import trader, instrument
from datetime import datetime, date, time

class TestTrader(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.sample_instrument = instrument.Instrument(
            instrument.InstrumentIdentification(isin="IRO1FOLD0001", tsetmc_code="46348559193224090", 
                                                ticker="فولاد"))
        self.sample_date = date(year=2023, month=4, day=30)
        super().__init__(*args, **kwargs)

    def test_portfolio_asset_dynamics(self):
        portfolio = trader.Portfolio()
        portfolio.update_asset(isin=self.sample_instrument.identification.isin, quantity=100)
        self.assertTrue(portfolio.get_asset_quantity(self.sample_instrument.identification.isin) == 100)
        portfolio.update_asset(isin=self.sample_instrument.identification.isin, quantity=200)
        self.assertTrue(portfolio.get_asset_quantity(self.sample_instrument.identification.isin) == 200)
        self.assertTrue(portfolio.get_asset(self.sample_instrument.identification.isin).quantity == 200)
        portfolio.remove_asset(isin=self.sample_instrument.identification.isin)
        self.assertTrue(portfolio.get_asset_quantity(self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_asset(self.sample_instrument.identification.isin) is None)
        portfolio.update_asset(isin=self.sample_instrument.identification.isin, quantity=300)
        self.assertTrue(portfolio.get_asset_quantity(self.sample_instrument.identification.isin) == 300)
        portfolio.empty_asset()
        self.assertTrue(portfolio.get_asset_quantity(self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_asset(self.sample_instrument.identification.isin) is None)

    def test_portfolio_position_dynamics(self):
        portfolio = trader.Portfolio()
        portfolio.update_position(isin=self.sample_instrument.identification.isin, quantity=-100)
        self.assertTrue(portfolio.get_position_quantity(self.sample_instrument.identification.isin) == -100)
        portfolio.update_position(isin=self.sample_instrument.identification.isin, quantity=-200)
        self.assertTrue(portfolio.get_position_quantity(self.sample_instrument.identification.isin) == -200)
        self.assertTrue(portfolio.get_position(self.sample_instrument.identification.isin).quantity == -200)
        portfolio.remove_position(isin=self.sample_instrument.identification.isin)
        self.assertTrue(portfolio.get_position_quantity(self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_position(self.sample_instrument.identification.isin) is None)
        portfolio.update_position(isin=self.sample_instrument.identification.isin, quantity=-300)
        self.assertTrue(portfolio.get_position_quantity(self.sample_instrument.identification.isin) == -300)
        portfolio.empty_position()
        self.assertTrue(portfolio.get_position_quantity(self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_position(self.sample_instrument.identification.isin) is None)
        
if __name__ == '__main__':
    unittest.main()