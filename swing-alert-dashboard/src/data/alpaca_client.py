"""Alpaca historical bar fetch for stocks and crypto."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from src.config import Config

CRYPTO_SUFFIX = "/USD"


def is_crypto_symbol(symbol: str) -> bool:
    return "/" in symbol or symbol.endswith(CRYPTO_SUFFIX)


def _create_stock_client(config: Config) -> StockHistoricalDataClient:
    if not config.alpaca_api_key or not config.alpaca_secret_key:
        raise ValueError("Missing Alpaca credentials in .env")
    return StockHistoricalDataClient(
        api_key=config.alpaca_api_key,
        secret_key=config.alpaca_secret_key,
    )


def _create_crypto_client(config: Config) -> CryptoHistoricalDataClient:
    if not config.alpaca_api_key or not config.alpaca_secret_key:
        raise ValueError("Missing Alpaca credentials in .env")
    return CryptoHistoricalDataClient(
        api_key=config.alpaca_api_key,
        secret_key=config.alpaca_secret_key,
    )


def fetch_bars(
    config: Config,
    symbol: str,
    *,
    days: int = 400,
    timeframe: TimeFrame = TimeFrame.Day,
) -> pd.DataFrame:
    """Fetch OHLCV bars for a stock or crypto symbol."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    if is_crypto_symbol(symbol):
        client = _create_crypto_client(config)
        request = CryptoBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
        )
        bars = client.get_crypto_bars(request)
    else:
        client = _create_stock_client(config)
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
        )
        bars = client.get_stock_bars(request)

    df = bars.df
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol, level="symbol")

    return df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]].sort_index()
