"""Test the models in tse_utils library"""
import unittest
from datetime import datetime, date
from tse_utils.models import trader, instrument, realtime, enums


class TestModels(unittest.TestCase):
    """Test the models in tse_utils library"""

    def __init__(self, *args, **kwargs):
        self.sample_instrument = instrument.Instrument(
            instrument.InstrumentIdentification(
                isin="IRO1FOLD0001",
                tsetmc_code="46348559193224090",
                ticker="فولاد"
            ))
        self.sample_date = date(year=2023, month=4, day=30)
        super().__init__(*args, **kwargs)

    def test_initiate_option_instrument(self):
        """Test initiation of an option instrument"""
        sample_option = instrument.OptionInstrument(
            exercise_date=date(year=2023, month=10, day=18),
            exercise_price=1819,
            underlying=self.sample_instrument,
            identification=instrument.InstrumentIdentification(
                isin="IRO9FOLD6831",
                ticker="ضفلا7021",
                tsetmc_code="34929123529054163"
            )
        )
        self.assertTrue(sample_option.exercise_price == 1819)
        self.assertTrue(
            sample_option.underlying.identification.isin == "IRO1FOLD0001"
        )

    def test_portfolio_asset_dynamics(self):
        """Test dynamics of portfolio assets"""
        portfolio = trader.Portfolio()
        portfolio.update_asset(
            trader.PortfolioSecurity(
                isin=self.sample_instrument.identification.isin,
                quantity=100
            ))
        self.assertTrue(portfolio.get_asset_quantity(
            self.sample_instrument.identification.isin) == 100)
        portfolio.update_asset(
            trader.PortfolioSecurity(
                isin=self.sample_instrument.identification.isin,
                quantity=200
            ))
        self.assertTrue(portfolio.get_asset_quantity(
            self.sample_instrument.identification.isin) == 200)
        self.assertTrue(portfolio.get_asset(
            self.sample_instrument.identification.isin).quantity == 200)
        portfolio.remove_asset(isin=self.sample_instrument.identification.isin)
        self.assertTrue(portfolio.get_asset_quantity(
            self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_asset(
            self.sample_instrument.identification.isin) is None)
        portfolio.update_asset(
            trader.PortfolioSecurity(
                isin=self.sample_instrument.identification.isin,
                quantity=300
            ))
        self.assertTrue(portfolio.get_asset_quantity(
            self.sample_instrument.identification.isin) == 300)
        portfolio.empty_asset()
        self.assertTrue(portfolio.get_asset_quantity(
            self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_asset(
            self.sample_instrument.identification.isin) is None)

    def test_portfolio_position_dynamics(self):
        """Test dynamics of portfolio positions"""
        portfolio = trader.Portfolio()
        portfolio.update_position(
            trader.PortfolioSecurity(
                isin=self.sample_instrument.identification.isin,
                quantity=-100
            ))
        self.assertTrue(portfolio.get_position_quantity(
            self.sample_instrument.identification.isin) == -100)
        portfolio.update_position(
            trader.PortfolioSecurity(
                isin=self.sample_instrument.identification.isin,
                quantity=-200
            ))
        self.assertTrue(portfolio.get_position_quantity(
            self.sample_instrument.identification.isin) == -200)
        self.assertTrue(portfolio.get_position(
            self.sample_instrument.identification.isin).quantity == -200)
        portfolio.remove_position(
            isin=self.sample_instrument.identification.isin)
        self.assertTrue(portfolio.get_position_quantity(
            self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_position(
            self.sample_instrument.identification.isin) is None)
        portfolio.update_position(
            trader.PortfolioSecurity(
                isin=self.sample_instrument.identification.isin,
                quantity=-300
            ))
        self.assertTrue(portfolio.get_position_quantity(
            self.sample_instrument.identification.isin) == -300)
        portfolio.empty_position()
        self.assertTrue(portfolio.get_position_quantity(
            self.sample_instrument.identification.isin) == 0)
        self.assertTrue(portfolio.get_position(
            self.sample_instrument.identification.isin) is None)

    def test_deep_order_book_dynamics(self):
        """Test dynamics of deep order books"""
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
        self.assertTrue(
            buy_rows[0].price == 1000 and buy_rows[0].volume == 100 and buy_rows[0].num == 1)
        self.assertTrue(
            buy_rows[1].price == 950 and buy_rows[1].volume == 200 and buy_rows[1].num == 2)
        self.assertTrue(
            sell_rows[0].price == 1010 and sell_rows[0].volume == 110 and sell_rows[0].num == 10)
        self.assertTrue(
            sell_rows[1].price == 1060 and sell_rows[1].volume == 210 and sell_rows[1].num == 20)
        # Update
        deep_order_book.remove_buy_row(price=950)
        deep_order_book.remove_buy_row(price=940)
        deep_order_book.remove_sell_row(price=1060)
        deep_order_book.remove_sell_row(price=1070)
        buy_rows = deep_order_book.get_buy_rows()
        sell_rows = deep_order_book.get_sell_rows()
        self.assertTrue(
            buy_rows[1].price == 900 and buy_rows[1].volume == 300 and buy_rows[1].num == 3)
        self.assertTrue(
            sell_rows[1].price == 1110 and sell_rows[1].volume == 310 and sell_rows[1].num == 30)
        # Empty
        deep_order_book.empty_buy_rows()
        deep_order_book.empty_sell_rows()
        buy_rows = deep_order_book.get_buy_rows()
        sell_rows = deep_order_book.get_sell_rows()
        self.assertFalse(buy_rows)
        self.assertFalse(sell_rows)

    def test_trader_order_dynamics(self):
        """Test dynamics of orders"""
        class ImplementedTrader(trader.Trader):
            """A sample from abstract trader class"""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            async def connect(self) -> None:
                pass

            async def connect_looper(
                    self,
                    interval: int = 3,
                    max_trial=10
            ) -> None:
                pass

            async def disconnect(self) -> None:
                pass

            async def get_server_datetime(self) -> datetime:
                pass

            async def pull_trader_data(self):
                pass

            async def subscribe_instruments_list(
                    self,
                    instruments: list[instrument.Instrument]
            ):
                pass

            async def order_send(self, order: trader.Order):
                pass

            async def order_cancel(self, order: trader.Order):
                pass

            async def order_edit(self, order: trader.Order, quantity: int, price: int):
                pass

        sample_trader = ImplementedTrader(
            credentials=trader.TraderCredentials(
                api=trader.TradingAPI(),
                username="aaa"
            )
        )
        # Initiation
        sample_trader.add_order(trader.Order(
            oms_id=1,
            isin=self.sample_instrument.identification.isin,
            side=enums.TradeSide.BUY,
            quantity=10,
            price=5
        ))
        sample_trader.add_order(trader.Order(
            oms_id=2,
            isin=self.sample_instrument.identification.isin,
            side=enums.TradeSide.SELL,
            quantity=20,
            price=30
        ))
        sample_trader.add_order(trader.Order(
            oms_id=3,
            isin=self.sample_instrument.identification.isin,
            side=enums.TradeSide.BUY,
            quantity=30,
            price=20
        ))
        sample_trader.add_order(trader.Order(
            oms_id=4,
            isin=self.sample_instrument.identification.isin,
            side=enums.TradeSide.BUY,
            quantity=40,
            price=20
        ))
        self.assertTrue(sample_trader.get_order(1).quantity == 10)
        self.assertTrue(sample_trader.get_order(4).quantity == 40)
        self.assertTrue(sample_trader.get_order_custom(
            lambda x: x.side == enums.TradeSide.SELL).oms_id == 2)
        self.assertTrue(sample_trader.get_order_custom(
            lambda x: x.price == 20).oms_id == 3)
        self.assertIsNone(sample_trader.get_order(5))
        self.assertIsNone(sample_trader.get_order_custom(
            lambda x: x.quantity == 100))
        all_orders = sample_trader.get_orders()
        buy_orders = sample_trader.get_orders(
            lambda x: x.side == enums.TradeSide.BUY)
        self.assertTrue(len(all_orders) == 4)
        self.assertTrue(len(buy_orders) == 3)
        # Edition
        sample_order = sample_trader.get_order_custom(
            lambda x: x.quantity == 30)
        sample_order.price = 25
        sample_order.quantity = 35
        self.assertTrue(sample_trader.get_order_custom(
            lambda x: x.price == 20).oms_id == 4)
        self.assertTrue(sample_trader.get_order_custom(
            lambda x: x.quantity == 35).price == 25)
        # Deletion
        sample_trader.remove_order(3)
        self.assertIsNone(sample_trader.get_order_custom(
            lambda x: x.quantity == 35))
        # Emptying
        self.assertTrue(sample_trader.get_orders())
        sample_trader.empty_orders()
        self.assertFalse(sample_trader.get_orders())


if __name__ == '__main__':
    unittest.main()
