import os
import logging
from logging.handlers import RotatingFileHandler


BINANCE_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_SCR = os.environ.get("BINANCE_SCR_KEY")

REPORT_FILENAME = "report.txt"

PERSISTANT_PRICE_FILE = "last_evaluated_prices.json"
TRADED_ASSETS_FILE = "traded_asset_amounts.json"

LOG_FILENAME = "trader.log"

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=20971520,
                encoding="utf-8", backupCount=50)
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
log_format = "%(asctime)s %(filename)20s [%(levelname)5s]:%(lineno)3d: %(message)s"
formatter = logging.Formatter(log_format, datefmt="%d-%m-%Y %H:%M:%S")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# assets owned
ASSETS_OWNED = ("ETH", "ADA", "DOT", "VET", "DOGE")

# list of assets to be traded
ASSETS_TO_TRADE = ("ADAUSDT", "VETUSDT")

# locked amounts in wallets
WALLET_BALANCES = {"ETH": 0.1, "ADA": 100}

# amount of investment in TL
INVESTMENT = 0

# initial amount of USDT to start trading
INITIAL_USDT_INVESTMENT = 120

TRADED_ASSET_AMOUNTS = {

    "ADAUSDT": 0,
    "VETUSDT": 0,
    "USDT": 120
}

from utils import CheckInterval

ASSET_ORDER_THRESHOLDS = {

    "ADAUSDT": {
        CheckInterval.INTERVAL_10_SEC: {
            "buy": (-0.08, 10), # (percent decrease, amount to buy)
            "sell": (0.04, 10)  # (percent increase, amount to sell)
        },
        CheckInterval.INTERVAL_10_MIN: {
            "buy": (-0.1, 10),
            "sell": (0.07, 10)
        },
        CheckInterval.INTERVAL_30_MIN: {
            "buy": (-0.3, 10),
            "sell": (0.1, 10)
        },
        CheckInterval.INTERVAL_1_HOUR: {
            "buy": (-0.5, 10),
            "sell": (0.5, 10)
        },
        CheckInterval.INTERVAL_12_HOURS: {
            "buy": (-2, 10),
            "sell": (2, 20)
        }
    },

    "VETUSDT": {
        CheckInterval.INTERVAL_10_SEC: {
            "buy": (-0.05, 200), # (percent decrease, amount to buy)
            "sell": (0.05, 200)  # (percent increase, amount to sell)
        },
        CheckInterval.INTERVAL_10_MIN: {
            "buy": (-0.1, 200),
            "sell": (0.07, 300)
        },
        CheckInterval.INTERVAL_30_MIN: {
            "buy": (-0.3, 200),
            "sell": (0.5, 400)
        },
        CheckInterval.INTERVAL_1_HOUR: {
            "buy": (-0.5, 200),
            "sell": (0.7, 500)
        },
        CheckInterval.INTERVAL_12_HOURS: {
            "buy": (-3, 500),
            "sell": (4, 1000)
        }
    }
}