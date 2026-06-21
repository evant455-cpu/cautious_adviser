"""Environment variables and trading constants."""

from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

# Risk and sizing
RISK_PER_TRADE_PCT = 0.01
PORTFOLIO_HEAT_CAP_PCT = 0.06

# ATR multipliers
ATR_STOP_MULTIPLIER = 2.0
ATR_TRAIL_MULTIPLIER = 3.0
CHANDELIER_ATR_MULTIPLIER = 3.0

# Regime filter
REGIME_FAST_MA = 50
REGIME_SLOW_MA = 200

# Momentum confirmation thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70


@dataclass(frozen=True)
class Config:
    alpaca_api_key: str
    alpaca_secret_key: str
    alpaca_base_url: str
    pushover_user_key: str
    pushover_api_token: str
    paper_trading: bool = True
    watchlist: tuple[str, ...] = ()


def _parse_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_watchlist(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(symbol.strip().upper() for symbol in value.split(",") if symbol.strip())


def load_config() -> Config:
    load_dotenv()

    return Config(
        alpaca_api_key=os.getenv("ALPACA_API_KEY", ""),
        alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY", ""),
        alpaca_base_url=os.getenv("ALPACA_BASE_URL", ""),
        pushover_user_key=os.getenv("PUSHOVER_USER_KEY", ""),
        pushover_api_token=os.getenv("PUSHOVER_API_TOKEN", ""),
        paper_trading=_parse_bool(os.getenv("PAPER_TRADING"), default=True),
        watchlist=_parse_watchlist(os.getenv("WATCHLIST")),
    )
