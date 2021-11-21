from binance.streams import ThreadedWebsocketManager
from binance.enums import *
from twisted.internet import reactor

from config import ASSETS_TO_TRADE, logger
from price_statistics import PriceStatistics
from utils import MonitoringStartError


class PriceMonitor:

    def __init__(self):

        self._asset_price_data = {}
        self._assets_traded = ASSETS_TO_TRADE
        self._socket_mgr = ThreadedWebsocketManager()
        self._price_statistics = PriceStatistics()
        self._total_errors = 0

    def start_monitoring(self):
        """Start monitoring prices for traded symbols

        Raises MonitoringStartError if at least one of the sockets
        is not started successfully.
        """

        logger.info("Start monitoring prices...")

        try:
            self._socket_mgr.start()

            for asset in self._assets_traded:
                self._socket_mgr.start_symbol_ticker_socket(callback=self._price_msg_handler, symbol=asset)

            self._socket_mgr.join()

        except:
            raise MonitoringStartError("Failed to start socket!")

    def stop_monitoring(self):
        """Close the websocket connections and stop monitoring"""

        logger.info("Stop monitoring prices...")
        self._socket_mgr.stop()

        # properly terminate WebSocket
        reactor.stop()

        while reactor.running:
            pass

        self._conn_keys = []

    def _price_msg_handler(self, message):
        """Handle message from symbol ticker socket

        Symbol, close price, previous day close price, price change, and
        price change percent values are used from the incoming message.
        They are sent to PriceStatistics instance to process.

        :type message: dict
        :param message: Socket message dictionary
        """

        if message['e'] != 'error':
            self._asset_price_data["symbol"] = message["s"]
            self._asset_price_data["close"] = float(message["c"])
            self._asset_price_data["close_prev_day"] = float(message["x"])
            self._asset_price_data["change"] = float(message["p"])
            self._asset_price_data["change_percent"] = float(message["P"])

            self._log_incoming_message(self._asset_price_data)

            self._price_statistics.process_price(self._asset_price_data)

        else:
            logger.error(f"Error received from symbol ticker socket!")
            self._total_errors += 1

            if self._total_errors > 10:
                self._handle_msg_error()

    def _log_incoming_message(self, msg_data):
        """Print asset price message details

        :type msg_data: dict
        :param msg_data: Asset price data dictionary
        """

        logger.info(f"Symbol: {msg_data['symbol']}, "
                    f"Close Price: {msg_data['close']}, "
                    f"Prev. Day Close Price: {msg_data['close_prev_day']}, "
                    f"Change: {msg_data['change']}, "
                    f"Change percent: {msg_data['change_percent']}")

    def _handle_msg_error(self):
        """Handle message error"""

        logger.error("Total errors from symbol ticker socket reached 10!")
        self._total_errors = 0

        self.stop_monitoring()