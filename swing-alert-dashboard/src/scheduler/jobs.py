"""Scheduled scan jobs."""

from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import Config, load_config
from src.data.alpaca_client import fetch_bars
from src.notifications.pushover_client import send_notification
from src.signals.entry_signals import evaluate_entry

logger = logging.getLogger(__name__)


def run_scan(config: Config | None = None) -> list[str]:
    """Scan watchlist symbols and return alert messages."""
    config = config or load_config()
    alerts: list[str] = []

    for symbol in config.watchlist:
        try:
            bars = fetch_bars(config, symbol)
            if bars.empty:
                logger.warning("No bars returned for %s", symbol)
                continue

            signal = evaluate_entry(symbol, bars["close"])
            if signal:
                msg = f"{signal.signal_type.upper()} @ {signal.price:.2f} — {signal.reason}"
                alerts.append(f"{symbol}: {msg}")
                logger.info("Signal: %s", alerts[-1])
        except Exception:
            logger.exception("Scan failed for %s", symbol)

    return alerts


def notify_alerts(config: Config, alerts: list[str]) -> None:
    if not alerts:
        return
    send_notification(
        config,
        title="Swing Alert",
        message="\n".join(alerts),
    )


def scan_and_notify(config: Config | None = None) -> None:
    config = config or load_config()
    alerts = run_scan(config)
    notify_alerts(config, alerts)


def start_scheduler(config: Config | None = None) -> None:
    """Run a daily scan after the US market close (4:30 PM ET, Mon–Fri)."""
    config = config or load_config()
    scheduler = BlockingScheduler()

    scheduler.add_job(
        scan_and_notify,
        trigger=CronTrigger(day_of_week="mon-fri", hour=16, minute=30, timezone="America/New_York"),
        kwargs={"config": config},
        id="daily_scan",
        replace_existing=True,
    )

    logger.info("Scheduler started — daily scan at 16:30 ET")
    scheduler.start()
