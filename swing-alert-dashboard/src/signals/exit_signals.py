"""
Exit logic - PROJECT_PLAN.pdf section 2.1, Tier 1.

Three pieces, used together once a trade is open:
1. Structural stop - set once at entry, defines the 1R risk unit. Never moves.
2. Chandelier trailing stop - ratchets up only, starting from entry.
3. Profit target - a fixed R-multiple above entry, set once at entry.

The operative stop at any point is the higher of (1) and (2) - the
structural stop is the floor; the trailing stop only ever tightens
protection above it, never loosens it (PROJECT_PLAN.pdf: this trailing
stop "never moves against you").
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def structural_stop_pullback(low: pd.Series, lookback: int = 10) -> pd.Series:
    """Stop below the swing low for a pullback entry: the lowest low over
    the trailing `lookback` bars including the entry bar itself."""
    return low.rolling(window=lookback, min_periods=lookback).min()


def structural_stop_breakout(low: pd.Series, lookback_period: int = 20) -> pd.Series:
    """Stop below the broken-out range for a breakout entry: the lowest
    low of the prior `lookback_period` bars (today excluded) - the same
    consolidation range whose high defined the breakout level in
    entry_signals.breakout_entry_signal."""
    return low.shift(1).rolling(window=lookback_period, min_periods=lookback_period).min()


def chandelier_trailing_stop(chandelier_raw: pd.Series, entry_index: int) -> pd.Series:
    """Ratchets the raw Chandelier Exit level (indicators.atr.chandelier_exit_long)
    so it only ever moves up from the prior bar's value, starting at
    `entry_index` - PROJECT_PLAN.pdf section 2.1: this trailing stop "never
    moves against you." NaN before entry_index."""
    result = pd.Series(np.nan, index=chandelier_raw.index)
    if entry_index >= len(chandelier_raw):
        return result

    running_max = chandelier_raw.iloc[entry_index]
    result.iloc[entry_index] = running_max
    for i in range(entry_index + 1, len(chandelier_raw)):
        candidate = chandelier_raw.iloc[i]
        if pd.notna(candidate) and (pd.isna(running_max) or candidate > running_max):
            running_max = candidate
        result.iloc[i] = running_max
    return result


def current_stop(structural_stop_price: float, trailing_stop: pd.Series) -> pd.Series:
    """The operative stop at each point: the higher of the fixed
    structural stop (the 1R floor, set once at entry, never moves) and the
    ratcheted Chandelier trailing stop. NaN wherever the trailing stop is
    NaN (e.g. before entry, or before the Chandelier indicator itself has
    enough history)."""
    return trailing_stop.clip(lower=structural_stop_price)


def profit_target(entry_price: float, stop_price: float, r_multiple: float = 2.5) -> float:
    """Profit target at `r_multiple` x the initial risk (entry - stop)
    above entry - PROJECT_PLAN.pdf section 2.1: 2-3R, with 2.5R as this
    project's MVP default (config.PROFIT_TARGET_R_MULTIPLE)."""
    risk_per_unit = entry_price - stop_price
    return entry_price + r_multiple * risk_per_unit


def is_stopped_out(low: pd.Series, stop: pd.Series) -> pd.Series:
    """True on any bar where price traded through the current stop level -
    the bar's low fell at or below it. NaN stop values (e.g. before entry)
    resolve to False, not NaN, via the same pandas NaN-comparison behavior
    used throughout this project."""
    return low <= stop


def is_target_hit(high: pd.Series, target: float) -> pd.Series:
    """True on any bar where price traded at or through the profit target."""
    return high >= target
