# Cautious Adviser

A daily swing-trading **alert scanner** in Python. It looks for entries and exits on a watchlist of stocks and crypto, applies risk rules, and is designed to notify you by phone (Pushover). It sends alerts only; it contains no order-placement code.

The project lives in [`swing-alert-dashboard/`](swing-alert-dashboard/). The design is written up in [`PROJECT_PLAN.pdf`](swing-alert-dashboard/PROJECT_PLAN.pdf).

## What it does

- **Regime filter:** only considers trades when price is above a rising 50/200-day moving average.
- **Entry signals:** pullback-to-EMA and volume-confirmed breakout.
- **Exit signals:** structural stop, ratcheting Chandelier (ATR-based) trailing stop, and a profit target.
- **Risk controls:** 1% position sizing, per-name concentration cap, and a 6% portfolio "heat" cap (total risk across open positions).
- **Alert formatting:** entry and exit messages ready to send.
- **Data:** historical bars from Alpaca (IEX feed), verified against the live API.

## Status

Built and covered by tests: indicators, regime filter, entry and exit signals, risk modules, alert formatting, Alpaca bar fetching.

Not built yet: the scheduler (`scheduler/jobs.py`) and the main entry point (`main.py`) are placeholders, so the pieces are not yet wired into one running scanner.

## Run the tests

```bash
cd swing-alert-dashboard
python -m venv .venv
.venv\Scripts\activate        # Windows (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
pytest tests/
```

API keys go in a git-ignored `.env` file (copy `.env.example`). Never commit real keys.

## Stack

Python, pandas, numpy, pytest, APScheduler (for the planned scheduler), Alpaca market data, Pushover notifications.

## Disclaimer

Educational project. Nothing here is financial advice.
