from abc import ABC, abstractmethod

from config import logger
from utils import (OrderType,
                   CheckInterval,
                   get_asset_interval_strategy,
                   is_stop_condition_reached,
                   is_assets_available_for_decision,
                   stop_trading)
from account import account
from reporter import reporter
from market_order.factory import MarketOrderFactory


class Strategy(ABC):

    def __init__(self):

        self.order_factory = MarketOrderFactory()

    @abstractmethod
    def perform(self, change_percents, asset_stats):
        """Perform determined strategy according to price change percents

        :type change_percents: dict
        :param change_percents: Change percentages for the traded symbols
        :type asset_stats: dict
        :param asset_stats: Asset price statistics
        """
        pass

    def _perform_strategy_for(self, interval, change_percents, asset_stats):

        symbol = None
        amount = None
        order_type = OrderType.NO_ORDER

        for asset, change_percent in change_percents.items():
            logger.info(f"{asset} has change percent value of {change_percent}")

            asset_strategy = get_asset_interval_strategy(asset, interval, change_percent)
            logger.debug(f"{asset} - asset_strategy: {asset_strategy}")

            decision = asset_strategy[0]
            if decision == "BUY":
                logger.info(f"Decided to buy for {asset}")
                order_type = OrderType.BUY_ORDER
                symbol = asset
                amount = asset_strategy[1]

            elif decision == "SELL":
                logger.info(f"Decided to sell for {asset}")
                order_type = OrderType.SELL_ORDER
                symbol = asset
                amount = asset_strategy[1]

            else:
                logger.info(f"Decided NOT to buy or sell for {asset}")

            if is_stop_condition_reached(asset_stats):
                logger.info("===== STOP CONDITION REACHED =====")
                reporter.log_current_account_info(account)
                reporter.log_traded_asset_amounts()
                stop_trading()
            else:
                if decision:
                    if is_assets_available_for_decision(asset, amount, decision, asset_stats):
                        order = self.order_factory.get_order(order_type)
                        order.set_parameters(symbol, amount, asset_stats[asset].get("latest_price"))
                        order.add()
                    else:
                        logger.info("There is not enough amount of assets to buy/sell!")


class Interval10SecStrategy(Strategy):

    def perform(self, change_percents, asset_stats):
        """Perform strategy for the 10 seconds interval"""

        logger.info("Performing strategy for 10 seconds interval...")
        self._perform_strategy_for(CheckInterval.INTERVAL_10_SEC, change_percents, asset_stats)

class Interval10MinStrategy(Strategy):

    def perform(self, change_percents, asset_stats):
        """Perform strategy for the 10 minutes interval"""

        logger.info("Performing strategy for 10 minutes interval...")
        self._perform_strategy_for(CheckInterval.INTERVAL_10_MIN, change_percents, asset_stats)

class Interval30MinStrategy(Strategy):

    def perform(self, change_percents, asset_stats):
        """Perform strategy for the 30 minutes interval"""

        logger.info("Performing strategy for 30 minutes interval...")
        self._perform_strategy_for(CheckInterval.INTERVAL_30_MIN, change_percents, asset_stats)

class Interval1HourStrategy(Strategy):

    def perform(self, change_percents, asset_stats):
        """Perform strategy for the 1 hour interval"""

        logger.info("Performing strategy for 1 hour interval...")
        self._perform_strategy_for(CheckInterval.INTERVAL_1_HOUR, change_percents, asset_stats)

class Interval12HoursStrategy(Strategy):

    def perform(self, change_percents, asset_stats):
        """Perform strategy for the 12 hours interval"""

        logger.info("Performing strategy for 12 hours interval...")
        self._perform_strategy_for(CheckInterval.INTERVAL_12_HOURS, change_percents, asset_stats)
