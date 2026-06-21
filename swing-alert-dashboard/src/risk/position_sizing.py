"""
Position sizing - PROJECT_PLAN.pdf section 2.3.

The 1% rule: risk a fixed fraction of equity per trade, sized off the
actual stop distance, not a fixed share count. Also includes the
concentration cap (no single position too large, independent of the risk
cap) since it's a trivial, directly related calculation.
"""
from __future__ import annotations


def position_size(equity: float, entry_price: float, stop_price: float, risk_pct: float) -> float:
    """Shares (or coins) to buy so that a stop-out risks exactly
    `risk_pct` of `equity` - PROJECT_PLAN.pdf section 2.3: size = (equity
    x risk%) / (entry - stop). Returns a raw float; the caller decides
    whether to round for whole-share assets vs. leave fractional for
    crypto (Alpaca supports fractional orders for both).

    Raises ValueError if stop_price >= entry_price - a stop at or above
    entry is not a valid long setup, and silently returning 0 or a
    negative size would be worse than failing loudly here."""
    risk_per_share = entry_price - stop_price
    if risk_per_share <= 0:
        raise ValueError(
            f"stop_price ({stop_price}) must be below entry_price ({entry_price}) "
            "for a long position - this would not produce a valid risk distance."
        )
    risk_amount = equity * risk_pct
    return risk_amount / risk_per_share


def position_value(shares: float, entry_price: float) -> float:
    """Total dollar value of a position at entry."""
    return shares * entry_price


def exceeds_concentration_cap(position_value_: float, equity: float, cap: float) -> bool:
    """True if this position alone would exceed `cap` fraction of equity
    (PROJECT_PLAN.pdf section 2.3: no single position over ~10-20% of
    portfolio value, independent of the risk cap). Uses a small epsilon
    so floating-point representation error doesn't falsely flag a
    position landing exactly at the cap (see portfolio_heat.py for the
    same issue hit concretely in testing)."""
    EPSILON = 1e-9
    return (position_value_ / equity) > (cap + EPSILON)
