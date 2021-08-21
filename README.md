trader
======

Trading bot running on Binance written for educational/exploratory purposes.

**Warning: Since this code contains highly customized trading strategy, DO NOT use it for real trading.**


Requirements
------------

Run one of the following commands to install dependencies

* `pipenv install`
* `pip install -r requirements.txt`

* Define `BINANCE_API_KEY` and `BINANCE_SCR_KEY` environment variables.

* Configure `ASSETS_OWNED`, `ASSETS_TO_TRADE`, `WALLET_BALANCES`, `INVESTMENT`,
`INITIAL_USDT_INVESTMENT`, `TRADED_ASSET_AMOUNTS`, and `ASSET_ORDER_THRESHOLDS`
values according to your needs inside config.py.


Usage
-----
`python trader.py`
