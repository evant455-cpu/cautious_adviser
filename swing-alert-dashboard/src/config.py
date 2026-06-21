"""
Central configuration for the swing-trading alert dashboard.

Loads credentials from .env and defines every tunable constant used by the
indicator, signal, and risk modules. This file performs no I/O beyond
reading environment variables on import, so it's always safe to import
(including from tests) even before .env is filled in. Credential presence
is only enforced when validate_credentials() is called explicitly - do
that once, at startup, in main.py or the connectivity check.

Parameter choices here trace back to Section 2 of PROJECT_PLAN.pdf
(the evidence-based rule set). Don't change a value here without updating
that document.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY", "")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN", "")


def validate_credentials() -> None:
    required = {
        "ALPACA_API_KEY": ALPACA_API_KEY,
        "ALPACA_SECRET_KEY": ALPACA_SECRET_KEY,
        "PUSHOVER_USER_KEY": PUSHOVER_USER_KEY,
        "PUSHOVER_API_TOKEN": PUSHOVER_API_TOKEN,
    }
    missing = [name for name, val in required.items() if not val]
    if missing:
        raise ConfigError(
            "Missing required environment variables: " + ", ".join(missing)
            + ". Copy .env.example to .env and fill these in."
        )


RISK_PCT_PER_TRADE: float = 0.005
PORTFOLIO_HEAT_CAP: float = 0.06
CONCENTRATION_CAP: float = 0.15
MIN_REWARD_RISK: float = 2.0
BTC_CORRELATION_THRESHOLD: float = 0.7

REGIME_FAST_MA: int = 50
REGIME_SLOW_MA: int = 200

PULLBACK_EMA_PERIODS: tuple[int, ...] = (20, 50)
BREAKOUT_VOLUME_MULTIPLIER: float = 1.5

ATR_PERIOD: int = 22
ATR_MULTIPLIER: dict[str, float] = {
    "stock": 3.0,
    "crypto": 4.0,
}
PROFIT_TARGET_R_MULTIPLE: float = 2.5

STOCK_UNIVERSE: list[str] = []
CRYPTO_UNIVERSE: list[str] = ["BTC/USD", "ETH/USD"]


def asset_class(symbol: str) -> str:
    return "crypto" if "/" in symbol else "stock"
