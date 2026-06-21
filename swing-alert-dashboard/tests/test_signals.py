import numpy as np
import pandas as pd

from src.signals.entry_signals import breakout_entry, evaluate_entry, pullback_entry
from src.signals.exit_signals import compute_exit_levels, structural_stop
from src.signals.regime_filter import regime_allows_long


def _bullish_close(length: int = 260) -> pd.Series:
    idx = pd.date_range("2023-01-01", periods=length, freq="D")
    values = np.linspace(80, 160, length) + np.sin(np.linspace(0, 8, length))
    return pd.Series(values, index=idx)


def test_regime_allows_long_in_uptrend():
    close = _bullish_close()
    assert regime_allows_long(close)


def test_breakout_detects_new_high():
    close = pd.Series([10, 10, 10, 10, 11])
    assert breakout_entry(close, lookback=3) is True


def test_structural_stop_below_entry():
    stop = structural_stop(entry_price=100.0, atr_value=2.0, multiplier=2.0)
    assert stop == 96.0


def test_compute_exit_levels_ordering():
    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    close = pd.Series(np.linspace(100, 120, 60), index=idx)
    high = close + 1
    low = close - 1

    levels = compute_exit_levels(100.0, high, low, close)
    assert levels.structural_stop < 100.0 < levels.profit_target


def test_evaluate_entry_returns_none_without_regime():
    close = pd.Series(np.linspace(160, 80, 260))
    assert evaluate_entry("SPY", close) is None
