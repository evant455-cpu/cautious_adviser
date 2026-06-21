"""Pushover notification client."""

from __future__ import annotations

import requests

from src.config import Config

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


def send_notification(config: Config, title: str, message: str, *, priority: int = 0) -> None:
    if not config.pushover_user_key or not config.pushover_api_token:
        raise ValueError("Missing Pushover credentials in .env")

    response = requests.post(
        PUSHOVER_URL,
        data={
            "token": config.pushover_api_token,
            "user": config.pushover_user_key,
            "title": title,
            "message": message,
            "priority": priority,
        },
        timeout=10,
    )
    response.raise_for_status()
