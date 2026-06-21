import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from src.signals.entry_signals import (
    is_bullish_engulfing,
    is_hammer,
    is_bullish_reversal_candle,
    pullback_entry_signal,
    breakout_entry_signal,
)


def test_bullish_engulfing_true_case():
    open_ = pd.Series([10.0, 7.0])
    close = pd.Series([8.0, 11.0])
    result = is_bullish_engulfing(open_, close)
    assert result.tolist() == [False, True]


def test_bullish_engulfing_false_when_body_not_fully_engulfed():
    open_ = pd.Series([10.0, 9.0])
    close = pd.Series([8.0, 9.5])
    result = is_bullish_engulfing(open_, close)
    assert result.tolist() == [False, False]


def test_hammer_true_case():
    o = pd.Series([10.0])
    h = pd.Series([10.3])
    l = pd.Series([8.0])
    c = pd.Series([10.2])
    assert is_hammer(o, h, l, c).tolist() == [True]


def test_hammer_false_when_upper_wick_too_long():
    o = pd.Series([10.0])
    h = pd.Series([12.0])
    l = pd.Series([9.9])
    c = pd.Series([10.2])
    assert is_hammer(o, h, l, c).tolist() == [False]


def test_hammer_false_for_doji():
    o = pd.Series([10.0])
    h = pd.Series([10.1])
    l = pd.Series([8.0])
    c = pd.Series([10.0])
    assert is_hammer(o, h, l, c).tolist() == [False]


def test_reversal_candle_is_either_pattern():
    o = pd.Series([10.0, 6.5])
    h = pd.Series([10.3, 9.5])
    l = pd.Series([8.0, 6.0])
    c = pd.Series([10.2, 9.0])
    result = is_bullish_reversal_candle(o, h, l, c)
    assert bool(result.iloc[0]) is True


def test_pullback_entry_fires_when_all_conditions_met():
    open_ = pd.Series([9.0, 9.0, 9.0, 10.0])
    high = pd.Series([9.5, 9.5, 9.5, 10.3])
    low = pd.Series([8.5, 8.5, 8.5, 8.0])
    close = pd.Series([9.2, 9.2, 9.2, 10.2])
    volume = pd.Series([100.0, 100.0, 100.0, 50.0])
    ema = pd.Series([8.5, 8.5, 8.5, 8.5])
    result = pullback_entry_signal(
        open_, high, low, close, volume, ema, volume_avg_period=3
    )
    assert bool(result.iloc[3]) is True


def test_pullback_entry_false_when_volume_not_declining():
    open_ = pd.Series([9.0, 9.0, 9.0, 10.0])
    high = pd.Series([9.5, 9.5, 9.5, 10.3])
    low = pd.Series([8.5, 8.5, 8.5, 8.0])
    close = pd.Series([9.2, 9.2, 9.2, 10.2])
    volume = pd.Series([100.0, 100.0, 100.0, 150.0])
    ema = pd.Series([8.5, 8.5, 8.5, 8.5])
    result = pullback_entry_signal(
        open_, high, low, close, volume, ema, volume_avg_period=3
    )
    assert bool(result.iloc[3]) is False


def test_pullback_entry_false_when_ema_not_touched():
    open_ = pd.Series([9.0, 9.0, 9.0, 10.0])
    high = pd.Series([9.5, 9.5, 9.5, 10.3])
    low = pd.Series([8.5, 8.5, 8.5, 9.5])
    close = pd.Series([9.2, 9.2, 9.2, 10.2])
    volume = pd.Series([100.0, 100.0, 100.0, 50.0])
    ema = pd.Series([8.5, 8.5, 8.5, 8.5])
    result = pullback_entry_signal(
        open_, high, low, close, volume, ema, volume_avg_period=3
    )
    assert bool(result.iloc[3]) is False


def test_pullback_entry_false_before_enough_volume_history():
    n = 5
    open_ = pd.Series([9.0] * n)
    high = pd.Series([9.5] * n)
    low = pd.Series([8.0] * n)
    close = pd.Series([9.2] * n)
    volume = pd.Series([50.0] * n)
    ema = pd.Series([8.5] * n)
    result = pullback_entry_signal(
        open_, high, low, close, volume, ema, volume_avg_period=20
    )
    assert not result.any()
    assert result.dtype == bool


def test_breakout_entry_fires_on_volume_confirmed_breakout():
    high = pd.Series([10.0] * 20 + [10.0, 10.0, 10.0, 10.0, 12.0])
    close = pd.Series([9.5] * 20 + [9.5, 9.5, 9.5, 9.5, 11.0])
    volume = pd.Series([100.0] * 20 + [100.0, 100.0, 100.0, 100.0, 200.0])
    result = breakout_entry_signal(
        high, close, volume, lookback_period=20, volume_multiplier=1.5, volume_avg_period=20
    )
    assert bool(result.iloc[24]) is True


def test_breakout_entry_false_without_volume_confirmation():
    high = pd.Series([10.0] * 20 + [10.0, 10.0, 10.0, 10.0, 12.0])
    close = pd.Series([9.5] * 20 + [9.5, 9.5, 9.5, 9.5, 11.0])
    volume = pd.Series([100.0] * 20 + [100.0, 100.0, 100.0, 100.0, 110.0])
    result = breakout_entry_signal(
        high, close, volume, lookback_period=20, volume_multiplier=1.5, volume_avg_period=20
    )
    assert bool(result.iloc[24]) is False


def test_breakout_entry_false_without_price_breakout():
    high = pd.Series([10.0] * 24 + [10.0])
    close = pd.Series([9.5] * 24 + [9.8])
    volume = pd.Series([100.0] * 24 + [300.0])
    result = breakout_entry_signal(
        high, close, volume, lookback_period=20, volume_multiplier=1.5, volume_avg_period=20
    )
    assert bool(result.iloc[24]) is False


def test_breakout_entry_false_before_enough_history():
    n = 10
    high = pd.Series([10.0] * n)
    close = pd.Series([11.0] * n)
    volume = pd.Series([500.0] * n)
    result = breakout_entry_signal(
        high, close, volume, lookback_period=20, volume_multiplier=1.5, volume_avg_period=20
    )
    assert not result.any()
    assert result.dtype == bool
