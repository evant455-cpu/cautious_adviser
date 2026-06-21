"""
Entry setups - PROJECT_PLAN.pdf section 2.2, Tier 1.

Both setups assume the caller has already confirmed the regime filter
(signals/regime_filter.py) is True for this bar - these functions only
detect the setup-specific pattern, they don't re-check trend/regime.
"""
from __future__ import annotations

import pandas as pd


def is_bullish_engulfing(open_: pd.Series, close: pd.Series) -> pd.Series:
    """Two-candle pattern: yesterday bearish, today bullish, and today's
    body fully engulfs yesterday's body."""
    prev_open = open_.shift(1)
    prev_close = close.shift(1)
    prev_bearish = prev_close < prev_open
    today_bullish = close > open_
    engulfs = (open_ < prev_close) & (close > prev_open)
    return prev_bearish & today_bullish & engulfs


def is_hammer(open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Single-candle pattern: small body near the top of the range, a
    lower wick at least twice the body size, and a minimal upper wick -
    the standard hammer definition."""
    body = (close - open_).abs()
    body_top = pd.concat([open_, close], axis=1).max(axis=1)
    body_bottom = pd.concat([open_, close], axis=1).min(axis=1)
    lower_wick = body_bottom - low
    upper_wick = high - body_top

    has_body = body > 0
    long_lower_wick = lower_wick >= 2 * body
    small_upper_wick = upper_wick <= body

    return has_body & long_lower_wick & small_upper_wick


def is_bullish_reversal_candle(
    open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series
) -> pd.Series:
    """Either a bullish engulfing or a hammer - the two reversal candles
    named in PROJECT_PLAN.pdf section 2.2."""
    return is_bullish_engulfing(open_, close) | is_hammer(open_, high, low, close)


def pullback_entry_signal(
    open_: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    ema: pd.Series,
    volume_avg_period: int = 20,
) -> pd.Series:
    """Pullback-to-EMA setup (section 2.2): price touches the EMA (the
    bar's low reaches at or below it) on below-average volume, and forms
    a bullish reversal candle that same bar. Pass whichever EMA you're
    testing (20, 21, or 50 per config.PULLBACK_EMA_PERIODS) - this
    function only detects the pattern, the caller picks the period and
    must AND this with the regime filter separately.

    Fires on the reversal-candle bar itself, not on a later breakout of
    its high - for an alerts-only system, surfacing the setup as soon as
    it forms is the right behavior; the human decides exact entry timing.
    PROJECT_PLAN.pdf's "or break of the reversal candle's high" is left
    as a manual decision, not automated here."""
    touched_ema = low <= ema
    avg_volume = volume.rolling(window=volume_avg_period, min_periods=volume_avg_period).mean()
    declining_volume = volume < avg_volume
    reversal_candle = is_bullish_reversal_candle(open_, high, low, close)

    return touched_ema & declining_volume & reversal_candle


def breakout_entry_signal(
    high: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    lookback_period: int = 20,
    volume_multiplier: float = 1.5,
    volume_avg_period: int = 20,
) -> pd.Series:
    """Volume-confirmed breakout setup (section 2.2): today's close clears
    the highest high of the prior `lookback_period` bars (today excluded),
    on volume at least `volume_multiplier` x the average of the prior
    `volume_avg_period` bars (today excluded). Volume is the deciding
    filter against false breakouts, per the project's research."""
    prior_high = high.shift(1).rolling(window=lookback_period, min_periods=lookback_period).max()
    breaks_out = close > prior_high

    prior_avg_volume = volume.shift(1).rolling(window=volume_avg_period, min_periods=volume_avg_period).mean()
    volume_confirmed = volume >= volume_multiplier * prior_avg_volume

    return breaks_out & volume_confirmed
