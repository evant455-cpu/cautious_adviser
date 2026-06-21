import numpy as np
import pandas as pd

from src.indicators.atr import atr, chandelier_exit
from src.indicators.momentum import macd, momentum_confirms_long, rsi
from src.indicators.moving_averages import ema, sma


def _sample_ohlc(length: int = 60) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    idx = pd.date_range("2024-01-01", periods=length, freq="D")
    close = pd.Series(np.linspace(100, 130, length) + np.random.default_rng(0).normal(0, 1, length), index=idx)
    high = close + 2
    low = close - 2
    open_ = close.shift(1).fillna(close.iloc[0])
    return open_, high, low, close


def test_sma_and_ema():
    _, _, _, close = _sample_ohlc()
    assert sma(close, 10).iloc[-1] > 0
    assert ema(close, 10).iloc[-1] > 0


def test_atr_positive():
    _, high, low, close = _sample_ohlc()
    values = atr(high, low, close)
    assert values.dropna().gt(0).all()


def test_chandelier_exit_long():
    _, high, low, close = _sample_ohlc()
    stop = chandelier_exit(high, low, close, direction="long")
    assert stop.dropna().iloc[-1] < close.iloc[-1]


def test_rsi_range():
    _, _, _, close = _sample_ohlc()
    values = rsi(close).dropna()
    assert values.between(0, 100).all()


def test_macd_columns():
    _, _, _, close = _sample_ohlc()
    frame = macd(close)
    assert set(frame.columns) == {"macd", "signal", "histogram"}


def test_momentum_confirms_long():
    assert momentum_confirms_long(55.0, 0.5) is True
    assert momentum_confirms_long(75.0, 0.5) is False
