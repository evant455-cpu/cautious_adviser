"""
Thin wrapper around Alpaca's trading client. Paper account only.
"""
from __future__ import annotations

from alpaca.trading.client import TradingClient

from src import config


def get_trading_client() -> TradingClient:
    return TradingClient(
        api_key=config.ALPACA_API_KEY,
        secret_key=config.ALPACA_SECRET_KEY,
        paper=True,
    )


def check_connection() -> dict:
    """Authenticate against the paper account and return basic account info.
    Raises whatever the SDK raises on auth failure - this is a diagnostic
    call, it should never fail silently."""
    client = get_trading_client()
    account = client.get_account()
    return {
        "account_number": account.account_number,
        "status": str(account.status),
        "equity": str(account.equity),
        "buying_power": str(account.buying_power),
    }


def get_bars(symbol: str, asset_class: str, lookback_days: int = 300) -> "pd.DataFrame":
    """
    Fetch daily OHLCV bars for one symbol from Alpaca, going back
    `lookback_days` calendar days. Returns a plain DataFrame indexed by
    date with columns: open, high, low, close, volume - ready to feed
    directly into the indicator/signal functions, which expect plain
    pandas Series, not Alpaca's multi-indexed BarSet.

    NOTE: unlike every other function in this project, this has not been
    independently verified against a live Alpaca account - there was no
    way to test real API responses without network access or
    credentials. Run a real smoke test against this specific function
    before trusting it in the scheduler.
    """
    from datetime import datetime, timedelta

    from alpaca.data.timeframe import TimeFrame

    end = datetime.utcnow()
    start = end - timedelta(days=lookback_days)

    if asset_class == "crypto":
        from alpaca.data.historical import CryptoHistoricalDataClient
        from alpaca.data.requests import CryptoBarsRequest

        client = CryptoHistoricalDataClient(
            api_key=config.ALPACA_API_KEY, secret_key=config.ALPACA_SECRET_KEY
        )
        request = CryptoBarsRequest(
            symbol_or_symbols=symbol, timeframe=TimeFrame.Day, start=start, end=end
        )
        bar_set = client.get_crypto_bars(request)
    else:
        from alpaca.data.enums import DataFeed
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest

        client = StockHistoricalDataClient(
            api_key=config.ALPACA_API_KEY, secret_key=config.ALPACA_SECRET_KEY
        )
        # Free/paper accounts only have access to the IEX feed - SIP is a
        # paid add-on (Algo Trader Plus). Without this, Alpaca defaults to
        # the "best" feed your subscription allows, and the default
        # resolution for recent dates is SIP, which a free account can't
        # query and fails with: "subscription does not permit querying
        # recent SIP data." Confirmed against the live API on 2026-06-22.
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
            feed=DataFeed.IEX,
        )
        bar_set = client.get_stock_bars(request)

    df = bar_set.df
    if hasattr(df.index, "levels"):  # MultiIndex (symbol, timestamp)
        df = df.loc[symbol]

    return df[["open", "high", "low", "close", "volume"]]
