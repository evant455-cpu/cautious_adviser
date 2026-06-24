"""
Live verification for alpaca_client.get_bars() - this function could not
be tested without network access to Alpaca, so this script is the first
real check of it. Run from the project root:
    python scripts/check_bars.py                 # checks AAPL + BTC/USD
    python scripts/check_bars.py AAPL stock      # checks one symbol
    python scripts/check_bars.py BTC/USD crypto  # checks one symbol
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.data.alpaca_client import get_bars


def _check_one(symbol: str, asset_class: str) -> None:
    print(f"\nFetching {symbol} ({asset_class})...")
    df = get_bars(symbol, asset_class, lookback_days=300)
    print("Columns:", list(df.columns))
    print("Index type:", type(df.index))
    print("Row count:", len(df))
    print("First row:\n", df.head(1))
    print("Last row:\n", df.tail(1))
    print("Any NaN in close column:", df["close"].isna().any())


def main() -> None:
    config.validate_credentials()

    if len(sys.argv) == 3:
        symbol, asset_class = sys.argv[1], sys.argv[2]
        _check_one(symbol, asset_class)
    else:
        _check_one("AAPL", "stock")
        _check_one("BTC/USD", "crypto")

    print("\nDone. Check that DataFrames have plausible row counts")
    print("(roughly 300 for crypto since it trades every day; somewhat")
    print("fewer for stocks since markets are closed weekends/holidays)")
    print("and that open/high/low/close/volume all look like real numbers,")
    print("not zeros, NaNs, or obviously wrong magnitudes.")


if __name__ == "__main__":
    main()
