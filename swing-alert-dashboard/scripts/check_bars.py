"""
Live verification for alpaca_client.get_bars() - this function could not
be tested without network access to Alpaca, so this script is the first
real check of it. Run from the project root:
    python scripts/check_bars.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.data.alpaca_client import get_bars


def main() -> None:
    config.validate_credentials()

    print("Fetching AAPL (stock)...")
    aapl = get_bars("AAPL", "stock", lookback_days=300)
    print("Columns:", list(aapl.columns))
    print("Index type:", type(aapl.index))
    print("Row count:", len(aapl))
    print("First row:\n", aapl.head(1))
    print("Last row:\n", aapl.tail(1))
    print("Any NaN in close column:", aapl["close"].isna().any())

    print("\nFetching BTC/USD (crypto)...")
    btc = get_bars("BTC/USD", "crypto", lookback_days=300)
    print("Columns:", list(btc.columns))
    print("Row count:", len(btc))
    print("Last row:\n", btc.tail(1))

    print("\nDone. Check that both DataFrames have plausible row counts")
    print("(roughly 300 for crypto since it trades every day; somewhat")
    print("fewer for AAPL since stock markets are closed weekends/holidays)")
    print("and that open/high/low/close/volume all look like real numbers,")
    print("not zeros, NaNs, or obviously wrong magnitudes.")


if __name__ == "__main__":
    main()
