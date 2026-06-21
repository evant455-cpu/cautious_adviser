"""Portfolio heat cap and BTC-correlation aggregation."""

from __future__ import annotations

from dataclasses import dataclass

from src.config import PORTFOLIO_HEAT_CAP_PCT

BTC_CORRELATED_SYMBOLS = frozenset(
    {
        "BTC/USD",
        "ETH/USD",
        "COIN",
        "MSTR",
        "MARA",
        "RIOT",
        "CLSK",
    }
)


@dataclass(frozen=True)
class OpenRisk:
    symbol: str
    risk_pct: float


def is_btc_correlated(symbol: str) -> bool:
    normalized = symbol.upper()
    if normalized in BTC_CORRELATED_SYMBOLS:
        return True
    return normalized.startswith("BTC") or normalized.startswith("ETH")


def total_heat(positions: list[OpenRisk]) -> float:
    return sum(position.risk_pct for position in positions)


def btc_correlated_heat(positions: list[OpenRisk]) -> float:
    return sum(position.risk_pct for position in positions if is_btc_correlated(position.symbol))


def can_add_position(
    positions: list[OpenRisk],
    *,
    new_risk_pct: float,
    heat_cap: float = PORTFOLIO_HEAT_CAP_PCT,
) -> bool:
    """Return True if adding new_risk_pct stays within the portfolio heat cap."""
    return total_heat(positions) + new_risk_pct <= heat_cap


def aggregate_btc_exposure(positions: list[OpenRisk]) -> float:
    """Combined heat from BTC-correlated positions."""
    return btc_correlated_heat(positions)
