from datetime import datetime
from config import REPORT_FILENAME, TRADED_ASSET_AMOUNTS


class Reporter:

    def __init__(self):

        self._separator = "*" * 80

    def log_current_account_info(self, account):
        """Log last state of the user account

        :type account: Account
        :param account: User account to report
        """

        log_str = (f"{self._get_current_date()}\n"
                   f"{str(account)}"
                   f"{self._separator}\n\n")

        self._write_log(log_str)

    def log_execution_result(self, order_result):
        """Log result of the market order execution

        :type order_result: dict
        :param order_result: Result of the order execution
        """

        log_str = (f"{self._get_current_date()}\n"
                   f"{order_result}\n"
                   f"{self._separator}\n\n")

        self._write_log(log_str)

    def log_traded_asset_amounts(self):
        """Log last state of the traded assets"""

        log_str = (f"{self._get_current_date()}\n"
                   f"TRADED_ASSET_AMOUNTS: {TRADED_ASSET_AMOUNTS}\n"
                   f"{self._separator}\n\n")

        self._write_log(log_str)

    def _get_current_date(self):
        """Get current date and time in human readable format

        :rtype: str
        :returns: Current date and time information
        """

        now = datetime.now()
        formatted_date = now.strftime("%d/%m/%Y %H:%M:%S")

        return formatted_date

    def _write_log(self, log_str):
        """Write the given log to report.txt file

        :type log_str: str
        :param log_str: Log string
        """

        with open(REPORT_FILENAME, "a") as report_file:
            report_file.write(log_str)


reporter = Reporter()