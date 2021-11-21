from time import sleep
from threading import Thread

from config import logger, ASSETS_TO_TRADE
from utils import CheckInterval, get_client
from persistant_stats import PersistantStats
from strategy.factory import StrategyFactory


class PriceEvaluator:

    def __init__(self, price_statistics):

        self._price_statistics = price_statistics
        self._persistant_stats = PersistantStats()
        self._strategy_factory = StrategyFactory()

        self._save_initial_prices()
        self._start_evaluators()

    def evaluate_ten_seconds_stats(self):
        """Compare latest price for every 10 seconds with the
        last evaluated price and create appropriate strategy.
        """

        logger.info("Starting 10 seconds evaluator...")

        while True:

            sleep(CheckInterval.INTERVAL_10_SEC)
            asset_stats = self._price_statistics.get_asset_stats()

            logger.info("Evaluating price change for 10 seconds interval...")

            change_percents = self._evaluate(CheckInterval.INTERVAL_10_SEC, asset_stats)

            self._execute_strategy(CheckInterval.INTERVAL_10_SEC, change_percents, asset_stats)

    def evaluate_ten_minutes_stats(self):
        """Compare latest price for every 10 minutes with the
        last evaluated price and create appropriate strategy.
        """

        logger.info("Starting 10 minutes evaluator...")

        while True:
            sleep(CheckInterval.INTERVAL_10_MIN)
            asset_stats = self._price_statistics.get_asset_stats()

            logger.info("Evaluating latest price for 10 minutes interval...")

            change_percents = self._evaluate(CheckInterval.INTERVAL_10_MIN, asset_stats)

            self._execute_strategy(CheckInterval.INTERVAL_10_MIN, change_percents, asset_stats)

    def evaluate_thirty_minutes_stats(self):
        """Compare latest price for every 30 minutes with the
        last evaluated price and create appropriate strategy.
        """

        logger.info("Starting 30 minutes evaluator...")

        while True:

            sleep(CheckInterval.INTERVAL_30_MIN)
            asset_stats = self._price_statistics.get_asset_stats()

            logger.info("Evaluating latest price for 30 minutes interval...")

            change_percents = self._evaluate(CheckInterval.INTERVAL_30_MIN, asset_stats)

            self._execute_strategy(CheckInterval.INTERVAL_30_MIN, change_percents, asset_stats)

    def evaluate_one_hour_stats(self):
        """Compare latest price for every 1 hour with the
        last evaluated price for this interval and create appropriate strategy.
        """

        logger.info("Starting 1 hour evaluator...")

        while True:

            sleep(CheckInterval.INTERVAL_1_HOUR)
            asset_stats = self._price_statistics.get_asset_stats()

            logger.info("Evaluating latest price for 1 hour interval...")

            change_percents = self._evaluate(CheckInterval.INTERVAL_1_HOUR, asset_stats)

            self._execute_strategy(CheckInterval.INTERVAL_1_HOUR, change_percents, asset_stats)

    def evaluate_twelve_hours_stats(self):
        """Compare latest price for every 12 hours with the
        last evaluated price for this interval and create appropriate strategy.
        """

        logger.info("Starting 12 hours evaluator...")

        while True:

            sleep(CheckInterval.INTERVAL_12_HOURS)
            asset_stats = self._price_statistics.get_asset_stats()

            logger.info("Evaluating latest price for 12 hours interval...")

            change_percents = self._evaluate(CheckInterval.INTERVAL_12_HOURS, asset_stats)

            self._execute_strategy(CheckInterval.INTERVAL_12_HOURS, change_percents, asset_stats)

    def _evaluate(self, interval, asset_stats):
        """Calculate the price change percentages of traded assets and
        save the latest price for the given interval.

        :type interval: CheckInterval
        :param interval: Price evaluation interval
        :type asset_stats: dict
        :param asset_stats: Asset price statistics
        :rtype: dict
        :returns: Change percentages for the symbols
        """

        change_percents = {}

        for symbol in asset_stats:
            latest_price = asset_stats[symbol].get("latest_price")
            change_percent = self._calculate_change_percent_for(symbol, interval, latest_price)
            change_percents[symbol] = change_percent

            logger.info(f"{symbol} price change percent for "
                        f"interval {interval} is {change_percent}")

            self._save(symbol, interval, latest_price)

        return change_percents

    def _execute_strategy(self, interval, change_percents, asset_stats):
        """Determine and perform strategy according to interval and
        price change percentages.

        :type interval: CheckInterval
        :param interval: Price evaluation interval
        :type change_percents: dict
        :param change_percents: Change percentages for the traded symbols
        :type asset_stats: dict
        :param asset_stats: Asset price statistics
        """

        strategy = self._strategy_factory.get_strategy(interval)
        strategy.perform(change_percents, asset_stats)

    def _start_evaluators(self):
        """Start evaluator methods as different threads"""

        evaluators = [self.evaluate_ten_seconds_stats,
                      self.evaluate_ten_minutes_stats,
                      self.evaluate_thirty_minutes_stats,
                      self.evaluate_one_hour_stats,
                      self.evaluate_twelve_hours_stats]

        for evaluator in evaluators:
            thread = Thread(target=evaluator, daemon=True)
            thread.start()

    def _calculate_change_percent_for(self, symbol, interval, latest_price):
        """Calculate the price change as percentage

        :type symbol: str
        :param symbol: Asset symbol
        :type interval: CheckInterval
        :param interval: Price evaluation interval
        :type latest_price: float
        :param latest_price: Asset latest price
        :rtype: float
        :returns: Price change percentage
        """

        previous = self._persistant_stats.get_previous_price_for(interval, symbol)
        change_percent = ((latest_price - previous) / previous) * 100

        return round(change_percent, 3)

    def _save_initial_prices(self):
        """Save initial price data"""

        client = get_client()
        initial_asset_prices = {}

        for asset_symbol in ASSETS_TO_TRADE:
            asset_price = client.get_symbol_ticker(symbol=asset_symbol).get("price")
            initial_asset_prices[asset_symbol] = float(asset_price)

        logger.info("Saving initial price data...")

        self._persistant_stats.save_initial_price_data(initial_asset_prices)

    def _save(self, symbol, interval, latest_price):
        """Save the latest price value for the given interval

        :type symbol: str
        :param symbol: Asset symbol
        :type interval: CheckInterval
        :param interval: Price evaluation interval
        :type latest_price: float
        :param latest_price: Asset latest price
        """

        logger.debug(f"Saving {symbol} latest_price[{latest_price}] for interval {interval}")

        self._persistant_stats.save(symbol, interval, latest_price)
