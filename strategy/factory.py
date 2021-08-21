from config import logger
from utils import CheckInterval

from strategy.strategies import (Interval10SecStrategy,
                                 Interval10MinStrategy,
                                 Interval30MinStrategy,
                                 Interval1HourStrategy,
                                 Interval12HoursStrategy)

class StrategyFactory:

    def get_strategy(self, interval):
        """Get strategy according to interval

        :type interval: CheckInterval
        :param interval: Price evaluation interval
        :rtype: Strategy
        :returns: Concrete strategy object
        """

        strategy = None

        if interval == CheckInterval.INTERVAL_10_SEC:
            strategy = Interval10SecStrategy()
        elif interval == CheckInterval.INTERVAL_10_MIN:
            strategy = Interval10MinStrategy()
        elif interval == CheckInterval.INTERVAL_30_MIN:
            strategy = Interval30MinStrategy()
        elif interval == CheckInterval.INTERVAL_1_HOUR:
            strategy = Interval1HourStrategy()
        elif interval == CheckInterval.INTERVAL_12_HOURS:
            strategy = Interval12HoursStrategy()
        else:
            logger.error("Invalid interval!")

        return strategy