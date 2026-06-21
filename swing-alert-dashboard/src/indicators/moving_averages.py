"""
Simple and exponential moving averages.

These back the regime filter (50/200-day MA - PROJECT_PLAN.pdf section 2.2)
and the pullback entry setup (20/21/50 EMA - section 2.2).
"""
from __future__ import annotations

import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple moving average over `period` bars. NaN until `period` bars
    of history exist."""
    return series.rolling(window=period, min_periods=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential moving average over `period` bars, using the standard
    recursive definition (alpha = 2 / (period + 1)), seeded with the first
    raw value - this matches how most charting platforms compute EMA.
    NaN until `period` bars of history exist."""
    return series.ewm(span=period, adjust=False, min_periods=period).mean()
