"""
RSI and MACD - confirmation-only signals (PROJECT_PLAN.pdf section 2.1,
Tier 3). Neither is a standalone entry or exit trigger in this system.
"""
from __future__ import annotations

import pandas as pd

from src.indicators.atr import wilder_smooth
from src.indicators.moving_averages import ema


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index, Wilder-smoothed over `period` bars
    (standard 14-period, per section 2.1)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = wilder_smooth(gain, period)
    avg_loss = wilder_smooth(loss, period)

    rs = avg_gain / avg_loss
    result = 100 - (100 / (1 + rs))
    # A Wilder-smoothed average loss of exactly 0 means no down moves at all
    # in the window - RSI is defined as 100 there, not NaN/inf.
    result = result.where(avg_loss != 0, 100.0)
    return result


def macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """MACD line, signal line, and histogram (standard 12/26/9, per
    section 2.1). Returns a DataFrame with columns: macd, signal, histogram."""
    fast_ema = ema(series, fast_period)
    slow_ema = ema(series, slow_period)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line - signal_line
    return pd.DataFrame(
        {"macd": macd_line, "signal": signal_line, "histogram": histogram}
    )
