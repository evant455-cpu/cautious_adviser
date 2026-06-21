"""
Trend/regime filter - PROJECT_PLAN.pdf section 2.2.

This is the single most important filter in the system: per the project's
research (Blokland's S&P 500 analysis, Pacer ETFs), price above a rising
200-day MA earns roughly +25% annualized on average, versus roughly -25%
below it. Every long entry setup in this system is gated behind this
filter - it's the primary defense against trading into chop.
"""
from __future__ import annotations

import pandas as pd

from src.indicators.moving_averages import sma


def is_rising(series: pd.Series, lookback: int = 5) -> pd.Series:
    """True where `series` is higher than it was `lookback` bars ago - a
    simple, low-noise definition of 'rising' for a moving average. False
    (not NaN) wherever there isn't enough history yet - pandas resolves
    NaN comparisons to False natively, so this needs no extra handling."""
    return series > series.shift(lookback)


def regime_filter(
    close: pd.Series,
    fast_period: int = 50,
    slow_period: int = 200,
    rising_lookback: int = 5,
) -> pd.Series:
    """True only when price is above BOTH a rising fast MA and a rising
    slow MA (default 50/200, per section 2.2). Bars without enough history
    to compute both MAs and their slope evaluate to False, not NaN - an
    ungated bar should never read as 'in regime' by default."""
    fast_ma = sma(close, fast_period)
    slow_ma = sma(close, slow_period)

    above_fast = close > fast_ma
    above_slow = close > slow_ma
    fast_rising = is_rising(fast_ma, rising_lookback)
    slow_rising = is_rising(slow_ma, rising_lookback)

    return above_fast & above_slow & fast_rising & slow_rising
