"""50/200 MA regime gate."""

from __future__ import annotations

import pandas as pd

from src.config import REGIME_FAST_MA, REGIME_SLOW_MA
from src.indicators.moving_averages import sma


def regime_allows_long(close: pd.Series) -> bool:
    """Bull regime: price above 50 SMA and 50 SMA above 200 SMA."""
    fast = sma(close, REGIME_FAST_MA)
    slow = sma(close, REGIME_SLOW_MA)
    if fast.isna().iloc[-1] or slow.isna().iloc[-1]:
        return False
    return close.iloc[-1] > fast.iloc[-1] > slow.iloc[-1]


def regime_allows_short(close: pd.Series) -> bool:
    """Bear regime: price below 50 SMA and 50 SMA below 200 SMA."""
    fast = sma(close, REGIME_FAST_MA)
    slow = sma(close, REGIME_SLOW_MA)
    if fast.isna().iloc[-1] or slow.isna().iloc[-1]:
        return False
    return close.iloc[-1] < fast.iloc[-1] < slow.iloc[-1]
