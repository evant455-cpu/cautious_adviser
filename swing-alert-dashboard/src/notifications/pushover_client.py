"""
Minimal Pushover client: one function, send a push notification.
"""
from __future__ import annotations

import requests

from src import config

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"


def send_notification(message: str, title: str | None = None) -> dict:
    """Send a push notification. Raises on any non-2xx response - alerts
    are the whole point of this system, so this should never fail silently."""
    payload = {
        "token": config.PUSHOVER_API_TOKEN,
        "user": config.PUSHOVER_USER_KEY,
        "message": message,
    }
    if title:
        payload["title"] = title

    response = requests.post(PUSHOVER_API_URL, data=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def format_entry_alert(
    symbol: str,
    asset_class: str,
    setup: str,
    entry_price: float,
    stop_price: float,
    target_price: float,
    size: float,
    portfolio_heat_after: float,
) -> str:
    """Body text for an entry alert. Every level is pre-committed before
    the human ever sees the alert - PROJECT_PLAN.pdf's defense against
    behavioral failure (moving stops, target creep) is that nothing here
    is decided in the moment."""
    risk_per_unit = entry_price - stop_price
    reward_per_unit = target_price - entry_price
    reward_risk_ratio = reward_per_unit / risk_per_unit if risk_per_unit else float("nan")
    unit_label = "shares" if asset_class == "stock" else "coins"

    return (
        f"{symbol} [{asset_class.upper()}] - {setup}\n"
        f"Entry: {entry_price:.2f}\n"
        f"Stop: {stop_price:.2f}  (risk {risk_per_unit:.2f}/unit)\n"
        f"Target: {target_price:.2f}  ({reward_risk_ratio:.1f}R)\n"
        f"Size: {size:.2f} {unit_label}\n"
        f"Portfolio heat after: {portfolio_heat_after:.2%}"
    )


def format_exit_alert(
    symbol: str,
    asset_class: str,
    reason: str,
    exit_price: float,
    entry_price: float,
) -> str:
    """Body text for an exit alert: why it exited, the level, and the
    realized return relative to entry."""
    pnl_pct = (exit_price - entry_price) / entry_price
    return (
        f"{symbol} [{asset_class.upper()}] - {reason.upper()}\n"
        f"Exit: {exit_price:.2f}  (entry was {entry_price:.2f}, {pnl_pct:+.2%})"
    )
