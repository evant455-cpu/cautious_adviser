"""Average True Range and Chandelier Exit."""

from __future__ import annotations

import pandas as pd


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    ranges = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr = true_range(high, low, close)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def chandelier_exit(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    *,
    period: int = 22,
    atr_period: int = 14,
    multiplier: float = 3.0,
    direction: str = "long",
) -> pd.Series:
    """Chandelier Exit trailing stop level."""
    atr_values = atr(high, low, close, period=atr_period)
    rolling_high = high.rolling(window=period, min_periods=period).max()
    rolling_low = low.rolling(window=period, min_periods=period).min()

    if direction == "long":
        return rolling_high - multiplier * atr_values
    if direction == "short":
        return rolling_low + multiplier * atr_values
    raise ValueError("direction must be 'long' or 'short'")
