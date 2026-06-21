"""Structural stop, trailing stop, and profit target exits."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config import ATR_STOP_MULTIPLIER, ATR_TRAIL_MULTIPLIER, CHANDELIER_ATR_MULTIPLIER
from src.indicators.atr import atr, chandelier_exit


@dataclass(frozen=True)
class ExitLevels:
    structural_stop: float
    trailing_stop: float
    profit_target: float


def structural_stop(
    entry_price: float,
    atr_value: float,
    *,
    multiplier: float = ATR_STOP_MULTIPLIER,
) -> float:
    """Initial stop below entry based on ATR."""
    return entry_price - multiplier * atr_value


def trailing_stop_level(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    *,
    multiplier: float = ATR_TRAIL_MULTIPLIER,
) -> float:
    """Latest Chandelier Exit level for a long position."""
    trail = chandelier_exit(
        high,
        low,
        close,
        multiplier=multiplier,
        direction="long",
    )
    return float(trail.iloc[-1])


def profit_target(
    entry_price: float,
    structural_stop_price: float,
    *,
    reward_risk: float = 2.0,
) -> float:
    """Target at a fixed reward-to-risk multiple."""
    risk = entry_price - structural_stop_price
    return entry_price + reward_risk * risk


def compute_exit_levels(
    entry_price: float,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> ExitLevels:
    atr_value = float(atr(high, low, close).iloc[-1])
    stop = structural_stop(entry_price, atr_value)
    trail = trailing_stop_level(
        high,
        low,
        close,
        multiplier=CHANDELIER_ATR_MULTIPLIER,
    )
    target = profit_target(entry_price, stop)
    return ExitLevels(structural_stop=stop, trailing_stop=trail, profit_target=target)
