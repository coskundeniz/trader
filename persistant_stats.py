import os
import json
from threading import Lock

from config import logger, PERSISTANT_PRICE_FILE
from utils import CheckInterval


class PersistantStats:

    def __init__(self):

        self._read_lock = Lock()
        self._write_lock = Lock()
        self._persistant_prices = {
                CheckInterval.INTERVAL_10_SEC: {},
                CheckInterval.INTERVAL_10_MIN: {},
                CheckInterval.INTERVAL_30_MIN: {},
                CheckInterval.INTERVAL_1_HOUR: {},
                CheckInterval.INTERVAL_12_HOURS: {}
            }

        if os.path.exists(PERSISTANT_PRICE_FILE):
            with open(PERSISTANT_PRICE_FILE, "r", encoding="utf8") as prices_file:

                logger.info("Loading last evaluated prices from file...")
                persistant_prices = json.load(prices_file)

                for key, value in persistant_prices.items():
                    self._persistant_prices[int(key)] = value

    def get_previous_price_for(self, interval, symbol):
        """Get current statistics for all symbols

        This data is accessed by the threads of PriceEvaluator class.

        :type symbol: str
        :param symbol: Asset symbol
        :type interval: CheckInterval
        :param interval: Price evaluation interval
        :rtype: float
        :returns: Latest saved price data for given interval and symbol
            {
                interval: {
                    "symbol": latest_price,
                    "symbol2": latest_price2
                }
            }
        """

        self._read_lock.acquire()
        previous_price = self._persistant_prices[interval][symbol]
        logger.debug(f"Previous price for symbol {symbol} is {previous_price}")
        self._read_lock.release()

        return previous_price

    def save_initial_price_data(self, initial_asset_prices):
        """Save initial data for referencing in the first evaluations

        :type initial_asset_prices: dict
        :param initial_asset_prices: Initial asset price data in the following format
            {
                "symbol": latest_price,
                "symbol2": latest_price2
            }
        """

        for symbol, latest_price in initial_asset_prices.items():
            logger.debug(f"Saving initial price {latest_price} for symbol {symbol}...")
            self._persistant_prices[CheckInterval.INTERVAL_10_SEC][symbol]   = latest_price
            self._persistant_prices[CheckInterval.INTERVAL_10_MIN][symbol]   = latest_price
            self._persistant_prices[CheckInterval.INTERVAL_30_MIN][symbol]   = latest_price
            self._persistant_prices[CheckInterval.INTERVAL_1_HOUR][symbol]   = latest_price
            self._persistant_prices[CheckInterval.INTERVAL_12_HOURS][symbol] = latest_price

    def save(self, symbol, interval, latest_price):
        """Save prices to json file

        :type symbol: str
        :param symbol: Asset symbol
        :type interval: CheckInterval
        :param interval: Price evaluation interval
        :type latest_price: float
        :param latest_price: Asset latest price
        """

        logger.debug(f"Saving... Price: {latest_price}, Symbol: {symbol}, "
                     f"Interval: {interval}, File: {PERSISTANT_PRICE_FILE}")

        with self._write_lock:
            self._persistant_prices[interval][symbol] = latest_price

            with open(PERSISTANT_PRICE_FILE, "w", encoding="utf8") as prices_file:
                json.dump(self._persistant_prices, prices_file, indent=4)