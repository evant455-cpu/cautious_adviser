# Swing Alert Dashboard

Daily swing-trading alert scanner with regime filtering, ATR-based risk controls, and Pushover notifications.

## Setup

```bash
cd swing-alert-dashboard
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env          # then fill in API keys
```

## Run

```bash
python -m src.main
```

## Tests

```bash
pytest tests/
```

## Architecture

| Module | Role |
|--------|------|
| `config.py` | Env vars and constants (risk %, ATR multipliers, heat cap) |
| `data/alpaca_client.py` | Historical bar fetch for stocks and crypto |
| `indicators/` | SMA/EMA, ATR/Chandelier, RSI/MACD (confirmation only) |
| `signals/` | 50/200 MA regime gate, entry/exit signal logic |
| `risk/` | 1% position sizing, 6% portfolio heat cap |
| `notifications/pushover_client.py` | Alert delivery |
| `scheduler/jobs.py` | Scheduled scan jobs |
