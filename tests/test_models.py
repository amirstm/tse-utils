import unittest, sys, asyncio
sys.path.append("..")
from tse_utils.models import trader, instrument, realtime
from datetime import datetime, date, time

class TestModels(unittest.TestCase):

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
        
    def test_deep_order_book_dynamics(self):
        deep_order_book = realtime.DeepOrderBook()
        # Initiation
        deep_order_book.update_buy_row(2, 200, 950)
        deep_order_book.update_buy_row(3, 300, 900)
        deep_order_book.update_buy_row(1, 100, 1000)
        deep_order_book.update_sell_row(20, 210, 1060)
        deep_order_book.update_sell_row(10, 110, 1010)
        deep_order_book.update_sell_row(30, 310, 1110)
        buy_rows = deep_order_book.get_buy_rows()
        sell_rows = deep_order_book.get_sell_rows()
        self.assertTrue(buy_rows[0].price == 1000 and buy_rows[0].volume == 100 and buy_rows[0].num == 1)
        self.assertTrue(buy_rows[1].price == 950 and buy_rows[1].volume == 200 and buy_rows[1].num == 2)
        self.assertTrue(sell_rows[0].price == 1010 and sell_rows[0].volume == 110 and sell_rows[0].num == 10)
        self.assertTrue(sell_rows[1].price == 1060 and sell_rows[1].volume == 210 and sell_rows[1].num == 20)
        # Update
        deep_order_book.remove_buy_row(price=950)
        deep_order_book.remove_buy_row(price=940)
        deep_order_book.remove_sell_row(price=1060)
        deep_order_book.remove_sell_row(price=1070)
        buy_rows = deep_order_book.get_buy_rows()
        sell_rows = deep_order_book.get_sell_rows()
        self.assertTrue(buy_rows[1].price == 900 and buy_rows[1].volume == 300 and buy_rows[1].num == 3)
        self.assertTrue(sell_rows[1].price == 1110 and sell_rows[1].volume == 310 and sell_rows[1].num == 30)
        # Empty
        deep_order_book.empty_buy_rows()
        deep_order_book.empty_sell_rows()
        buy_rows = deep_order_book.get_buy_rows()
        sell_rows = deep_order_book.get_sell_rows()
        self.assertFalse(buy_rows)
        self.assertFalse(sell_rows)

if __name__ == '__main__':
    unittest.main()