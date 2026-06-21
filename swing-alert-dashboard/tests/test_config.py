import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src import config


def test_constants_within_research_backed_ranges():
    assert 0 < config.RISK_PCT_PER_TRADE <= 0.01
    assert config.PORTFOLIO_HEAT_CAP == 0.06
    assert config.MIN_REWARD_RISK >= 2.0
    assert config.ATR_PERIOD == 22
    assert config.ATR_MULTIPLIER["stock"] < config.ATR_MULTIPLIER["crypto"]


def test_asset_class_classifier():
    assert config.asset_class("BTC/USD") == "crypto"
    assert config.asset_class("AAPL") == "stock"


def test_validate_credentials_raises_when_missing(monkeypatch):
    monkeypatch.setattr(config, "ALPACA_API_KEY", "")
    monkeypatch.setattr(config, "ALPACA_SECRET_KEY", "x")
    monkeypatch.setattr(config, "PUSHOVER_USER_KEY", "x")
    monkeypatch.setattr(config, "PUSHOVER_API_TOKEN", "x")
    with pytest.raises(config.ConfigError):
        config.validate_credentials()


def test_validate_credentials_passes_when_complete(monkeypatch):
    monkeypatch.setattr(config, "ALPACA_API_KEY", "k")
    monkeypatch.setattr(config, "ALPACA_SECRET_KEY", "s")
    monkeypatch.setattr(config, "PUSHOVER_USER_KEY", "u")
    monkeypatch.setattr(config, "PUSHOVER_API_TOKEN", "t")
    config.validate_credentials()
