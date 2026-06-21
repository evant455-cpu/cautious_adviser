"""1% risk position sizing."""

from __future__ import annotations

from src.config import RISK_PER_TRADE_PCT


def shares_for_risk(
    account_equity: float,
    entry_price: float,
    stop_price: float,
    *,
    risk_pct: float = RISK_PER_TRADE_PCT,
) -> int:
    """Size position so dollar risk equals risk_pct of account equity."""
    if entry_price <= 0 or account_equity <= 0:
        return 0

    risk_per_share = entry_price - stop_price
    if risk_per_share <= 0:
        return 0

    risk_dollars = account_equity * risk_pct
    return int(risk_dollars // risk_per_share)
