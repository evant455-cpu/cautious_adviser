"""Swing Alert Dashboard entry point."""

from __future__ import annotations

import argparse
import logging

from src.config import load_config
from src.scheduler.jobs import run_scan, scan_and_notify, start_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Swing Alert Dashboard")
    parser.add_argument(
        "--mode",
        choices=["scan", "notify", "schedule"],
        default="scan",
        help="scan: print signals; notify: send Pushover alerts; schedule: run daily job",
    )
    args = parser.parse_args()

    config = load_config()

    if args.mode == "scan":
        for alert in run_scan(config):
            print(alert)
    elif args.mode == "notify":
        scan_and_notify(config)
    else:
        start_scheduler(config)


if __name__ == "__main__":
    main()
