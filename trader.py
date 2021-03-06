from twisted.internet.error import ReactorNotRunning

from account import account
from price_monitor import PriceMonitor
from reporter import reporter
from config import logger
from utils import (MonitoringStartError,
                   get_client,
                   restore_traded_asset_amounts,
                   set_price_monitor,
                   stop_trading)


def main():

    client = get_client()

    logger.info(f"System status: {client.get_system_status()['msg'].upper()}")

    restore_traded_asset_amounts()

    reporter.log_current_account_info(account)
    reporter.log_traded_asset_amounts()

    try:
        price_monitor = PriceMonitor()
        set_price_monitor(price_monitor)
        price_monitor.start_monitoring()
    except MonitoringStartError as err:
        logger.error(err)
        raise SystemExit("Failed to start monitoring! Exiting...")
    except ReactorNotRunning:
        raise SystemExit(0)
    except Exception as exc:
        logger.error(exc)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        logger.info("Script stopped manually!")
        reporter.log_current_account_info(account)
        reporter.log_traded_asset_amounts()
        stop_trading()

