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
