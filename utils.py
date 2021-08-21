import os
import json
import requests
from enum import Enum
from bs4 import BeautifulSoup
from twisted.internet.error import ReactorNotRunning

from config import (logger,
                    INITIAL_USDT_INVESTMENT,
                    ASSETS_TO_TRADE,
                    TRADED_ASSET_AMOUNTS,
                    TRADED_ASSETS_FILE)


price_monitor_instance = None

class MonitoringStartError(Exception):
    pass


class CheckInterval:

    INTERVAL_10_SEC   = 10
    INTERVAL_10_MIN   = 10 * 60
    INTERVAL_30_MIN   = 30 * 60
    INTERVAL_1_HOUR   = 1 * 60 * 60
    INTERVAL_12_HOURS = 12 * 60 * 60


class OrderType(Enum):

    NO_ORDER = 0
    BUY_ORDER = 1
    SELL_ORDER = 2


def get_asset_interval_strategy(asset, interval, change_percent):
    """Get buy/sell decision and amount according for the given asset and interval

    :type asset: str
    :param asset: Asset symbol
    :type interval: CheckInterval
    :param interval: Price evaluation interval
    :type change_percent: dict
    :param change_percent: Change percentage for the asset
    """

    from config import ASSET_ORDER_THRESHOLDS

    target_values = ASSET_ORDER_THRESHOLDS.get(asset).get(interval)

    result = (None, None)

    if change_percent <= target_values["buy"][0]:
        result = ("BUY", target_values["buy"][1])

    if change_percent >= target_values["sell"][0]:
        result = ("SELL", target_values["sell"][1])

    return result


def is_assets_available_for_decision(asset, amount, decision, asset_stats):
    """Check if there are enough amounts of assets to execute decision

    :type asset: str
    :param asset: Asset symbol
    :type amount: float
    :param amount: Asset amount to buy/sell
    :type decision: str
    :param decision: BUY/SELL
    :type asset_stats: dict
    :param asset_stats: Asset price statistics
    :rtype: bool
    :returns: Whether there are enough amounts to execute decision
    """

    remaining_asset = TRADED_ASSET_AMOUNTS[asset]
    asset_current_price = asset_stats[asset].get("latest_price")
    current_usdt_amount = get_current_usdt_amount()

    if decision == "BUY":
        if amount * asset_current_price > current_usdt_amount:
            return False
    elif decision == "SELL":
        if remaining_asset < amount:
            return False
    else:
        return False

    return True


def is_stop_condition_reached(asset_stats):
    """Check if stop condition is reached

    If amount of total traded assets decreases more than half,
    stop trading.

    :type asset_stats: dict
    :param asset_stats: Asset price statistics
    :rtype: bool
    :returns: Whether stop trading or not
    """

    total_assets_as_usdt = calculate_total_for_traded_assets(asset_stats)

    return total_assets_as_usdt < (INITIAL_USDT_INVESTMENT / 2)


def calculate_total_for_traded_assets(asset_stats):
    """Calculate total as usdt

    :type asset_stats: dict
    :param asset_stats: Asset price statistics
    :rtype: float
    :returns: Total assets as usdt
    """

    total_as_usdt = get_current_usdt_amount()

    for asset in ASSETS_TO_TRADE:
        total_as_usdt += TRADED_ASSET_AMOUNTS[asset] * asset_stats[asset].get("latest_price")

    change = ((total_as_usdt - INITIAL_USDT_INVESTMENT) / INITIAL_USDT_INVESTMENT) * 100

    logger.info(f"Total traded asset amounts as usdt: {total_as_usdt}, change: {change} %")

    return total_as_usdt


def get_current_usdt_amount():
    """Get total usdt amount

    :type asset_stats: dict
    :param asset_stats: Asset price statistics
    :rtype: float
    :returns: Total usdt amount
    """

    return TRADED_ASSET_AMOUNTS["USDT"]


def update_traded_asset_amounts(symbol, amount, usdt_update_value):
    """Update asset amounts and save to the file

    :type symbol: str
    :param symbol: Asset symbol
    :type amount: float
    :param amount: Asset amount to buy/sell
    :type usdt_update_value: float
    :param usdt_update_value: USDT earned or spent from trade
    """

    TRADED_ASSET_AMOUNTS[symbol] += amount
    TRADED_ASSET_AMOUNTS["USDT"] += usdt_update_value

    usdt_amount = get_current_usdt_amount()
    logger.info(f"Updated {symbol} with amount={amount}. Current USDT amount={usdt_amount}")

    store_traded_asset_amounts()


def store_traded_asset_amounts():
    """Write current traded asset amounts to file as json"""

    logger.info(f"Storing updated values to {TRADED_ASSETS_FILE}...")

    with open(TRADED_ASSETS_FILE, "w", encoding="utf8") as traded_assets_file:
        json.dump(TRADED_ASSET_AMOUNTS, traded_assets_file, indent=4)

    logger.debug(f"Traded assets current amounts: {TRADED_ASSET_AMOUNTS}")


def restore_traded_asset_amounts():
    """Restore traded asset amounts from json file"""

    global TRADED_ASSET_AMOUNTS

    if os.path.exists(TRADED_ASSETS_FILE):
        with open(TRADED_ASSETS_FILE, "r", encoding="utf8") as traded_assets_file:

            logger.info(f"Restoring current values from {TRADED_ASSETS_FILE}...")
            TRADED_ASSET_AMOUNTS = json.load(traded_assets_file)

    logger.debug(f"Traded asset amounts at beginning: {TRADED_ASSET_AMOUNTS}")


def set_price_monitor(price_monitor):
    """Set price monitor instance globally

    :type price_monitor: PriceMonitor
    :param price_monitor: PriceMonitor instance
    """

    global price_monitor_instance

    price_monitor_instance = price_monitor


def stop_trading():
    """Stop monitoring prices and exit with error"""

    try:
        price_monitor_instance.stop_monitoring()
    except ReactorNotRunning:
        raise SystemExit(0)

    logger.info("Stop trading and exit!")

    raise SystemExit(1)


def get_current_dollar_exchange_rate():
    """Get current dollar exchange rate in TL

    :rtype: float
    :returns: current dollar value
    """

    parsed_page = _parse_page()

    assets = parsed_page.select(".item")[:3]
    dollar_value = assets[1].select("span.value")[0].text

    return float(dollar_value.replace(",", "."))


def _parse_page():
    """Open and parse page content

    :rtype: object
    :returns: BeautifulSoup object
    """

    PAGE_URL = "https://www.doviz.com"

    headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    try:
        response = requests.get(PAGE_URL, headers=headers)
    except requests.exceptions.RequestException as exc:
        logger.error(exc)
        raise SystemExit("Failed to get page!")
    else:
        parsed_page = BeautifulSoup(response.text, "html.parser")
        return parsed_page
