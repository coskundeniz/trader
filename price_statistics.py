from threading import Lock

from config import logger
from price_evaluator import PriceEvaluator


class PriceStatistics:

    def __init__(self):

        self._traded_asset_stats = {}
        self._stats_read_lock = Lock()
        self._evaluator = PriceEvaluator(self)

    def process_price(self, asset_price_data):
        """Process asset price data

        :type asset_price_data: dict
        :param asset_price_data: Asset price data in the following format
            {
                "symbol": str,
                "close": float,
                "close_prev_day": float,
                "change": float,
                "change_percent": float
            }
        """

        symbol = asset_price_data["symbol"]
        if symbol not in self._traded_asset_stats:
            self._traded_asset_stats[symbol] = {}

        self._traded_asset_stats[symbol]["prev_price"]     = self._traded_asset_stats[symbol].get("latest_price", 0.0)
        self._traded_asset_stats[symbol]["latest_price"]   = asset_price_data["close"]
        self._traded_asset_stats[symbol]["prev_day_price"] = asset_price_data["close_prev_day"]
        self._traded_asset_stats[symbol]["price_change"]   = asset_price_data["change"]
        self._traded_asset_stats[symbol]["change_percent"] = asset_price_data["change_percent"]

        logger.debug(self)

    def get_asset_stats(self):
        """Get current statistics for all symbols

        This data is accessed by the threads of PriceEvaluator class.

        :rtype: dict
        :returns: Asset price statistics in the following format
            {
                "symbol": {
                    "prev_price": float,
                    "latest_price": float,
                    "prev_day_price": float,
                    "price_change": float,
                    "change_percent": float
                }
            }
        """

        self._stats_read_lock.acquire()
        stats = self._traded_asset_stats
        self._stats_read_lock.release()

        return stats

    def __str__(self):

        result = "+++++++ PriceStatistics +++++++\n"

        for symbol in self._traded_asset_stats:
            result += f"*** {symbol} ***\n"

            result += f"Previous price: {self._traded_asset_stats[symbol]['prev_price']}\n"
            result += f"Latest price: {self._traded_asset_stats[symbol]['latest_price']}\n"
            result += f"Previous day price: {self._traded_asset_stats[symbol]['prev_day_price']}\n"
            result += f"Price change: {self._traded_asset_stats[symbol]['price_change']}\n"
            result += f"Price change percent: {self._traded_asset_stats[symbol]['change_percent']}\n\n"

        return result