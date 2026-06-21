"""
ATR (Average True Range) and the Chandelier Exit trailing stop.

ATR uses Wilder's smoothing - the practitioner/ChartSchool standard cited in
PROJECT_PLAN.pdf section 2.1: the first value is a simple average of the
first `period` true ranges, and every value after that follows
ATR_t = (ATR_(t-1) * (period - 1) + TR_t) / period.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """True range for each bar: the largest of today's high-low range,
    today's high vs. yesterday's close, and today's low vs. yesterday's close."""
    prev_close = close.shift(1)
    return pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def wilder_smooth(series: pd.Series, period: int) -> pd.Series:
    """Wilder's smoothing: seed with a simple average of the first `period`
    valid values, then recursively smooth. Returns NaN before the seed
    point. Tolerates a leading run of NaNs (e.g. from a diff()-based input
    like RSI's gain/loss series) by seeding from the first valid value
    rather than assuming index 0 is valid. Shared by ATR and RSI (both are
    defined with this smoothing method)."""
    values = series.to_numpy(dtype=float)
    n = len(values)
    out = np.full(n, np.nan)

    valid_mask = ~np.isnan(values)
    if valid_mask.sum() < period:
        return pd.Series(out, index=series.index)

    start = int(np.argmax(valid_mask))  # index of first non-NaN value
    seed_end = start + period  # exclusive
    if seed_end > n:
        return pd.Series(out, index=series.index)

    seed_window = values[start:seed_end]
    if np.isnan(seed_window).any():
        return pd.Series(out, index=series.index)

    out[seed_end - 1] = seed_window.mean()
    for i in range(seed_end, n):
        out[i] = (out[i - 1] * (period - 1) + values[i]) / period

    return pd.Series(out, index=series.index)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 22) -> pd.Series:
    """Average True Range, Wilder-smoothed over `period` bars (default 22,
    per PROJECT_PLAN.pdf section 2.1)."""
    tr = true_range(high, low, close)
    return wilder_smooth(tr, period)


def chandelier_exit_long(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 22,
    multiplier: float = 3.0,
) -> pd.Series:
    """Long-side Chandelier Exit: highest high over `period` bars minus
    (multiplier x ATR(period)). This returns the raw per-bar level only -
    when tracking an actual open position, the caller must take the running
    max of this value since entry, so the stop only ever moves up, never
    down (PROJECT_PLAN.pdf section 2.1)."""
    highest_high = high.rolling(window=period, min_periods=period).max()
    atr_values = atr(high, low, close, period=period)
    return highest_high - multiplier * atr_values
