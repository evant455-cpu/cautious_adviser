"""
Portfolio heat - PROJECT_PLAN.pdf section 2.3.

Tracks aggregate open risk across positions and blocks/flags new alerts
that would push total risk over the cap. Operates on plain lists of
already-computed per-position risk percentages - no position-tracking
data model exists yet in this project, so this stays deliberately simple
rather than inventing one prematurely.

NOTE: BTC-correlation aggregation ("treat BTC beta as one risk factor and
cap it") is explicitly a Phase 2 item per PROJECT_PLAN.pdf section 5.2,
not implemented here yet. Don't assume this module accounts for
correlated crypto exposure until that's built.
"""
from __future__ import annotations


def position_risk_pct(equity: float, entry_price: float, stop_price: float, shares: float) -> float:
    """The actual fraction of equity at risk for one position, given its
    real share count (useful when shares got rounded for a whole-share
    asset, so the realized risk may differ slightly from the target
    risk_pct passed to position_size())."""
    risk_amount = shares * (entry_price - stop_price)
    return risk_amount / equity


def portfolio_heat(position_risk_pcts: list[float]) -> float:
    """Total open risk across all current positions - PROJECT_PLAN.pdf
    section 2.3: capped at 6% aggregate."""
    return sum(position_risk_pcts)


def would_exceed_heat_cap(current_heat: float, new_position_risk_pct: float, heat_cap: float) -> bool:
    """True if adding a new position would push total portfolio heat
    strictly over `heat_cap` - landing exactly at the cap is allowed, only
    going over blocks the alert. Uses a small epsilon so floating-point
    representation error (e.g. 0.05 + 0.01 == 0.060000000000000005, not
    exactly 0.06) doesn't falsely block a position landing right at the
    cap."""
    EPSILON = 1e-9
    return (current_heat + new_position_risk_pct) > (heat_cap + EPSILON)
