"""Pullback and breakout entry signals."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.indicators.momentum import macd, momentum_confirms_long, rsi
from src.indicators.moving_averages import ema, sma
from src.signals.regime_filter import regime_allows_long


@dataclass(frozen=True)
class EntrySignal:
    symbol: str
    signal_type: str
    price: float
    reason: str


def pullback_entry(close: pd.Series, *, trend_period: int = 20) -> bool:
    """Price pulls back to the trend EMA in an uptrend and closes above it."""
    trend = ema(close, trend_period)
    if len(close) < trend_period + 2:
        return False

    prev_below = close.iloc[-2] <= trend.iloc[-2]
    now_above = close.iloc[-1] > trend.iloc[-1]
    uptrend = close.iloc[-1] > sma(close, 50).iloc[-1]
    return bool(prev_below and now_above and uptrend)


def breakout_entry(close: pd.Series, *, lookback: int = 20) -> bool:
    """Close breaks above the recent range high."""
    if len(close) < lookback + 1:
        return False
    range_high = close.iloc[-lookback - 1 : -1].max()
    return bool(close.iloc[-1] > range_high)


def evaluate_entry(symbol: str, close: pd.Series) -> EntrySignal | None:
    """Return an entry signal when regime, setup, and momentum align."""
    if not regime_allows_long(close):
        return None

    momentum = macd(close)
    rsi_value = float(rsi(close).iloc[-1])
    macd_hist = float(momentum["histogram"].iloc[-1])
    if not momentum_confirms_long(rsi_value, macd_hist):
        return None

    price = float(close.iloc[-1])

    if breakout_entry(close):
        return EntrySignal(symbol, "breakout", price, "Breakout above 20-day high with bullish regime")

    if pullback_entry(close):
        return EntrySignal(symbol, "pullback", price, "Pullback to 20 EMA in bullish regime")

    return None
