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
