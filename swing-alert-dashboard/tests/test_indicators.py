import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import pytest

from src.indicators.moving_averages import sma, ema
from src.indicators.atr import true_range, wilder_smooth, atr, chandelier_exit_long
from src.indicators.momentum import rsi, macd


def test_sma_known_values():
    s = pd.Series([1, 2, 3, 4, 5, 6], dtype=float)
    result = sma(s, period=3)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx((1 + 2 + 3) / 3)
    assert result.iloc[5] == pytest.approx((4 + 5 + 6) / 3)


def test_ema_matches_hand_calculation():
    s = pd.Series([10.0, 20.0, 30.0, 40.0])
    result = ema(s, period=3)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx(22.5)
    assert result.iloc[3] == pytest.approx(31.25)


def test_true_range_known_values():
    high = pd.Series([10.0, 12.0, 11.0])
    low = pd.Series([8.0, 9.0, 8.5])
    close = pd.Series([9.0, 11.5, 9.0])
    tr = true_range(high, low, close)
    assert tr.iloc[0] == pytest.approx(2.0)
    assert tr.iloc[1] == pytest.approx(3.0)
    assert tr.iloc[2] == pytest.approx(3.0)


def test_wilder_smooth_seed_is_simple_average():
    s = pd.Series([1.0, 2.0, 3.0, 10.0, 10.0])
    result = wilder_smooth(s, period=3)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx(2.0)
    assert result.iloc[3] == pytest.approx(14 / 3)
    expected = ((14 / 3) * 2 + 10) / 3
    assert result.iloc[4] == pytest.approx(expected)


def test_atr_first_value_is_simple_average_of_true_range():
    high = pd.Series([10.0, 12.0, 11.0, 13.0])
    low = pd.Series([8.0, 9.0, 8.5, 9.5])
    close = pd.Series([9.0, 11.5, 9.0, 12.0])
    tr = true_range(high, low, close)
    result = atr(high, low, close, period=3)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx(tr.iloc[0:3].mean())
    expected_next = (result.iloc[2] * 2 + tr.iloc[3]) / 3
    assert result.iloc[3] == pytest.approx(expected_next)


def test_chandelier_exit_matches_components():
    high = pd.Series([10.0, 12.0, 11.0, 13.0, 14.0])
    low = pd.Series([8.0, 9.0, 8.5, 9.5, 10.0])
    close = pd.Series([9.0, 11.5, 9.0, 12.0, 13.5])
    period, multiplier = 3, 2.0
    result = chandelier_exit_long(high, low, close, period=period, multiplier=multiplier)
    highest_high = high.rolling(window=period, min_periods=period).max()
    atr_values = atr(high, low, close, period=period)
    expected = highest_high - multiplier * atr_values
    pd.testing.assert_series_equal(result, expected)


def test_chandelier_exit_is_below_recent_highs():
    high = pd.Series([10.0, 12.0, 11.0, 13.0, 14.0, 15.0])
    low = pd.Series([8.0, 9.0, 8.5, 9.5, 10.0, 11.0])
    close = pd.Series([9.0, 11.5, 9.0, 12.0, 13.5, 14.0])
    result = chandelier_exit_long(high, low, close, period=3, multiplier=3.0)
    valid = result.dropna()
    assert (valid < high.loc[valid.index]).all()


def test_rsi_all_gains_is_100():
    s = pd.Series(np.arange(1, 30, dtype=float))
    result = rsi(s, period=14)
    valid = result.dropna()
    assert np.allclose(valid.to_numpy(), 100.0)


def test_rsi_all_losses_is_0():
    s = pd.Series(np.arange(30, 1, -1, dtype=float))
    result = rsi(s, period=14)
    valid = result.dropna()
    assert np.allclose(valid.to_numpy(), 0.0)


def test_rsi_first_value_matches_hand_calculation():
    s = pd.Series([10.0, 12.0, 11.0, 14.0])
    result = rsi(s, period=3)
    avg_gain = (2 + 0 + 3) / 3
    avg_loss = (0 + 1 + 0) / 3
    rs = avg_gain / avg_loss
    expected = 100 - (100 / (1 + rs))
    assert result.iloc[3] == pytest.approx(expected)


def test_macd_internal_consistency():
    s = pd.Series(np.linspace(10, 50, 60))
    result = macd(s, fast_period=12, slow_period=26, signal_period=9)
    assert list(result.columns) == ["macd", "signal", "histogram"]
    fast = ema(s, 12)
    slow = ema(s, 26)
    expected_macd_line = fast - slow
    pd.testing.assert_series_equal(result["macd"], expected_macd_line, check_names=False)
    expected_signal = ema(expected_macd_line, 9)
    pd.testing.assert_series_equal(result["signal"], expected_signal, check_names=False)
    pd.testing.assert_series_equal(
        result["histogram"], result["macd"] - result["signal"], check_names=False
    )
