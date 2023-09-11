from dataclasses import dataclass

@dataclass
class OrderBookRow():
    """
    Contains a single row from an instrument's order book
    """
    demand_num: int = 0
    demand_volume: int = 0
    demand_price: int = 0
    supply_num: int = 0
    supply_volume: int = 0
    supply_price: int = 0

    def __str__(self):
        return f"{self.supply_num} {self.supply_volume} {self.supply_price} | {self.demand_price} {self.demand_volume} {self.demand_num}"

class OrderBook():
    """
    Orderbook contains the top n rows of an instrument's orders on both sides
    """
    def __init__(self, row_count):
        self.orderbook_rows = [OrderBookRow() for i in range(row_count)]
    
    # def get_diff(self): TODO: get difference with order
