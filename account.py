from binance.client import Client

from config import (logger,
                    BINANCE_KEY,
                    BINANCE_SCR,
                    ASSETS_OWNED,
                    WALLET_BALANCES,
                    INVESTMENT)
from utils import get_current_dollar_exchange_rate


class Account:

    def __init__(self):

        self.client = Client(BINANCE_KEY, BINANCE_SCR)
        self.assets = ASSETS_OWNED
        self.asset_balances = {}
        self._benefit = 0
        self._total_in_tl = None

    def get_balance(self):
        """Get total asset value

        :rtype: dict
        :returns: Dictionary of asset_symbol: total_asset pairs
        """

        for symbol in self.assets:
            balance = self._get_asset_balance_for(symbol)
            self.asset_balances[symbol] = float(balance)

        for asset, balance in WALLET_BALANCES.items():
            self.asset_balances[asset] += float(balance)

        return self.asset_balances

    def calculate_total_in_tl(self):
        """Get total asset value and benefit in TL

        :rtype: tuple
        :returns: Total asset value and benefit in TL
        """

        balances = self.get_balance()

        total_asset_value_in_usd = self._get_total_in_usd(balances)
        total = sum(total_asset_value_in_usd.values())

        dolar_tl = get_current_dollar_exchange_rate()
        total_in_tl = total * dolar_tl
        self._benefit = total_in_tl - INVESTMENT
        logger.debug(f"Total: {total_in_tl} TL")
        logger.debug(f"Benefit: {self._benefit} TL")

        self._total_in_tl = (total_in_tl, self._benefit)

        return self._total_in_tl

    def get_benefit(self):
        """Get benefit in TL

        :rtype: int
        :returns: Total benefit in TL
        """

        return self._benefit

    def _get_total_in_usd(self, balances):
        """Get total asset value in USD

        :type balances: dict
        :param balances: Dictionary of asset_symbol: total_asset pairs
        :rtype: dict
        :returns: Dictionary of asset_symbol: total_value_in_usd pairs
        """

        total_asset_value_in_usd = {}
        for asset, balance in balances.items():
            asset_price = self.client.get_symbol_ticker(symbol=asset+"USDT").get("price")
            logger.info(f"Asset: {asset} - Balance: {balance}")
            logger.info(f"{asset+'USDT'}: {asset_price}")
            total_asset_value_in_usd[asset] = balance * float(asset_price)

        return total_asset_value_in_usd

    def _get_asset_balance_for(self, asset_symbol):
        """Get current asset balance for the given symbol

        :type asset_symbol: str
        :param asset_symbol: Asset symbol (e.g. ETH, ADA)
        :rtype: str
        :returns: Amount of total assets for given symbol
        """

        return self.client.get_asset_balance(asset=asset_symbol)["free"]

    def __str__(self):

        account_summary = "======= Account Summary =======\n"

        if not self.asset_balances:
            asset_balances = self.get_balance()
        else:
            asset_balances = self.asset_balances

        for asset, balance in asset_balances.items():
            account_summary += f"Asset: {asset} ## Balance: {balance}\n"

        if not self._total_in_tl:
            self._total_in_tl = self.calculate_total_in_tl()

        account_summary += f"Total: {self._total_in_tl[0]} TL\nBenefit: {self._total_in_tl[1]} TL\n"

        return account_summary


account = Account()