import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from src.signals.regime_filter import is_rising, regime_filter


def test_is_rising_true_for_uptrend():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    result = is_rising(s, lookback=3)
    assert bool(result.iloc[3]) is True
    assert bool(result.iloc[7]) is True


def test_is_rising_false_for_downtrend():
    s = pd.Series([8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0])
    result = is_rising(s, lookback=3)
    assert bool(result.iloc[3]) is False
    assert bool(result.iloc[7]) is False


def test_is_rising_false_for_flat_series():
    s = pd.Series([5.0] * 10)
    result = is_rising(s, lookback=3)
    assert not result.iloc[3:].any()


def test_is_rising_false_before_enough_history():
    s = pd.Series([1.0, 2.0, 3.0])
    result = is_rising(s, lookback=3)
    assert not result.any()
    assert result.dtype == bool


def test_regime_filter_true_in_clean_uptrend():
    n = 260
    close = pd.Series(100 + np.arange(n) * 0.5)
    result = regime_filter(close, fast_period=50, slow_period=200, rising_lookback=5)
    tail = result.iloc[210:]
    assert tail.all()
    assert tail.dtype == bool


def test_regime_filter_false_in_clean_downtrend():
    n = 260
    close = pd.Series(100 - np.arange(n) * 0.5)
    result = regime_filter(close, fast_period=50, slow_period=200, rising_lookback=5)
    tail = result.iloc[210:]
    assert not tail.any()


def test_regime_filter_false_when_flat():
    n = 260
    close = pd.Series([100.0] * n)
    result = regime_filter(close, fast_period=50, slow_period=200, rising_lookback=5)
    assert not result.any()


def test_regime_filter_false_before_enough_history():
    n = 100
    close = pd.Series(100 + np.arange(n) * 0.5)
    result = regime_filter(close, fast_period=50, slow_period=200, rising_lookback=5)
    assert not result.any()
    assert result.dtype == bool
    assert not result.isna().any()


def test_regime_filter_false_when_above_ma_but_ma_still_declining():
    decline = 200 - np.arange(220) * (100 / 219)
    recovery = 100 + np.arange(40) * 1.25
    close = pd.Series(np.concatenate([decline, recovery]))
    result = regime_filter(close, fast_period=50, slow_period=200, rising_lookback=5)
    assert not result.iloc[227:235].any()
