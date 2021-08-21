from utils import OrderType
from market_order.orders import (MarketBuyOrder,
                                 MarketSellOrder,
                                 MarketNoOrder)


class MarketOrderFactory:

    def get_order(self, order_type):
        """"Create order according to order types

        :type order_type: OrderType
        :param order_type: Type of order either buy, sell or no order
        """

        order = None
        if order_type == OrderType.BUY_ORDER:
            order = MarketBuyOrder()
        elif order_type == OrderType.SELL_ORDER:
            order = MarketSellOrder()
        else:
            order = MarketNoOrder()

        return order