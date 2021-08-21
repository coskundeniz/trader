from binance.client import Client
from binance.exceptions import (BinanceAPIException,
                                BinanceOrderException)
from config import logger, BINANCE_KEY, BINANCE_SCR
from utils import update_traded_asset_amounts
from executor import order_executor
from reporter import reporter


class MarketOrder:

    def __init__(self):

        self.symbol = None
        self.amount = 0.0
        self.client = Client(BINANCE_KEY, BINANCE_SCR)

    def set_parameters(self, symbol=None, amount=None, current_price=None):
        """Perform determined strategy according to price change percents

        :type symbol: str
        :param symbol: Asset symbol
        :type amount: float
        :param amount: Amount of asset to buy or sell
        """

        logger.info(f"Setting parameters... Symbol: {symbol}, Amount: {amount}, Price: {current_price}")
        self.symbol = symbol
        self.amount = amount
        self.current_price = current_price

    def add(self):
        """Add order to the Executer queue"""

        logger.info(f"Adding an order to executor queue...")
        order_executor.add_to_execution_queue(self)

    def execute_order(self):
        """Run order_market_buy/sell commands from Binance API"""
        pass


class MarketBuyOrder(MarketOrder):

    def execute_order(self):

        try:
            buy_result = self.client.order_market_buy(symbol=self.symbol, quantity=self.amount)
            logger.info(f"Order[{self}] executed successfully with id: [{buy_result['orderId']}]")
            usdt_spent = self.amount * self.current_price
            commission = float(buy_result["fills"][0].get("commission", 0))
            update_traded_asset_amounts(self.symbol, self.amount - commission, usdt_spent * (-1))
            reporter.log_execution_result(buy_result)
        except BinanceAPIException as e_api:
            logger.error(e_api)
        except BinanceOrderException as e_order:
            logger.error(e_order)
        except Exception as exp:
            logger.error(exp)

    def __str__(self):

        return f"BUY:{self.symbol}:{self.amount}:{self.current_price}"


class MarketSellOrder(MarketOrder):

    def execute_order(self):

        try:
            sell_result = self.client.order_market_sell(symbol=self.symbol, quantity=self.amount)
            logger.info(f"Order[{self}] executed successfully with id: [{sell_result['orderId']}]")
            commission = float(sell_result["fills"][0].get("commission", 0))
            usdt_earned = (self.amount * self.current_price) - commission
            update_traded_asset_amounts(self.symbol, self.amount * (-1), usdt_earned)
            reporter.log_execution_result(sell_result)
        except BinanceAPIException as e_api:
            logger.error(e_api)
        except BinanceOrderException as e_order:
            logger.error(e_order)
        except Exception as exp:
            logger.error(exp)

    def __str__(self):

        return f"SELL:{self.symbol}:{self.amount}:{self.current_price}"


class MarketNoOrder(MarketOrder):

    def set_parameters(self, symbol=None, amount=None, current_price=None):
        pass

    def add(self):
        pass

    def __str__(self):
        return ""
