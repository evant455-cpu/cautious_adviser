"""
One-time diagnostic: confirm Alpaca (paper) and Pushover credentials
actually work, before any signal logic is built on top of them.

Run from the project root:
    python scripts/check_connectivity.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.data.alpaca_client import check_connection
from src.notifications.pushover_client import send_notification


def main() -> None:
    config.validate_credentials()
    print("Credentials present. Checking Alpaca...")

    account = check_connection()
    print("Alpaca paper account reachable:")
    for key, value in account.items():
        print(f"  {key}: {value}")

    print("\nSending Pushover test notification...")
    result = send_notification(
        message="Swing dashboard connectivity check passed.",
        title="Swing Dashboard",
    )
    print("Pushover response:", result)
    print("\nAll connectivity checks passed.")


if __name__ == "__main__":
    main()
