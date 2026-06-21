import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import pytest

from src.signals.exit_signals import (
    structural_stop_pullback,
    structural_stop_breakout,
    chandelier_trailing_stop,
    current_stop,
    profit_target,
    is_stopped_out,
    is_target_hit,
)


def test_structural_stop_pullback_known_values():
    low = pd.Series([10.0, 8.0, 9.0, 7.0, 11.0])
    result = structural_stop_pullback(low, lookback=3)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx(min(10.0, 8.0, 9.0))
    assert result.iloc[3] == pytest.approx(min(8.0, 9.0, 7.0))
    assert result.iloc[4] == pytest.approx(min(9.0, 7.0, 11.0))


def test_structural_stop_breakout_excludes_current_bar():
    low = pd.Series([10.0, 8.0, 9.0, 7.0, 2.0])
    result = structural_stop_breakout(low, lookback_period=3)
    assert result.iloc[4] == pytest.approx(7.0)


def test_chandelier_trailing_stop_only_ratchets_up():
    raw = pd.Series([np.nan, 50.0, 55.0, 52.0, 60.0, 58.0])
    result = chandelier_trailing_stop(raw, entry_index=1)
    assert pd.isna(result.iloc[0])
    assert result.iloc[1] == pytest.approx(50.0)
    assert result.iloc[2] == pytest.approx(55.0)
    assert result.iloc[3] == pytest.approx(55.0)
    assert result.iloc[4] == pytest.approx(60.0)
    assert result.iloc[5] == pytest.approx(60.0)


def test_chandelier_trailing_stop_handles_nan_seed_at_entry():
    raw = pd.Series([np.nan, np.nan, 50.0, 48.0, 53.0])
    result = chandelier_trailing_stop(raw, entry_index=0)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx(50.0)
    assert result.iloc[3] == pytest.approx(50.0)
    assert result.iloc[4] == pytest.approx(53.0)


def test_chandelier_trailing_stop_nan_strictly_before_entry():
    raw = pd.Series([100.0, 110.0, 120.0])
    result = chandelier_trailing_stop(raw, entry_index=2)
    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx(120.0)


def test_current_stop_uses_structural_floor_until_trailing_exceeds_it():
    structural = 95.0
    trailing = pd.Series([np.nan, 90.0, 96.0, 99.0])
    result = current_stop(structural, trailing)
    assert pd.isna(result.iloc[0])
    assert result.iloc[1] == pytest.approx(95.0)
    assert result.iloc[2] == pytest.approx(96.0)
    assert result.iloc[3] == pytest.approx(99.0)


def test_profit_target_known_values():
    assert profit_target(entry_price=100.0, stop_price=95.0, r_multiple=2.0) == pytest.approx(110.0)
    assert profit_target(entry_price=50.0, stop_price=45.0, r_multiple=3.0) == pytest.approx(65.0)


def test_is_stopped_out():
    low = pd.Series([100.0, 98.0, 94.0, 96.0])
    stop = pd.Series([95.0, 95.0, 95.0, 95.0])
    result = is_stopped_out(low, stop)
    assert result.tolist() == [False, False, True, False]


def test_is_stopped_out_false_when_stop_is_nan():
    low = pd.Series([100.0, 50.0])
    stop = pd.Series([np.nan, np.nan])
    result = is_stopped_out(low, stop)
    assert result.tolist() == [False, False]
    assert result.dtype == bool


def test_is_target_hit():
    high = pd.Series([100.0, 109.0, 111.0])
    result = is_target_hit(high, target=110.0)
    assert result.tolist() == [False, False, True]
