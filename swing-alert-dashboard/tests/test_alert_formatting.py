import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.notifications.pushover_client import format_entry_alert, format_exit_alert


def test_format_entry_alert_stock_content():
    msg = format_entry_alert(
        symbol="AAPL", asset_class="stock", setup="pullback to 20 EMA",
        entry_price=180.00, stop_price=175.00, target_price=192.50,
        size=200.0, portfolio_heat_after=0.03,
    )
    assert "AAPL [STOCK] - pullback to 20 EMA" in msg
    assert "Entry: 180.00" in msg
    assert "Stop: 175.00" in msg
    assert "risk 5.00/unit" in msg
    assert "Target: 192.50" in msg
    assert "2.5R" in msg
    assert "Size: 200.00 shares" in msg
    assert "Portfolio heat after: 3.00%" in msg


def test_format_entry_alert_crypto_uses_coins_label():
    msg = format_entry_alert(
        symbol="BTC/USD", asset_class="crypto", setup="volume breakout",
        entry_price=50000.0, stop_price=48000.0, target_price=55000.0,
        size=0.02, portfolio_heat_after=0.045,
    )
    assert "BTC/USD [CRYPTO] - volume breakout" in msg
    assert "coins" in msg
    assert "shares" not in msg
    assert "Portfolio heat after: 4.50%" in msg


def test_format_entry_alert_reward_risk_ratio_known_value():
    msg = format_entry_alert(
        symbol="TEST", asset_class="stock", setup="breakout",
        entry_price=100.0, stop_price=90.0, target_price=130.0,
        size=10.0, portfolio_heat_after=0.01,
    )
    assert "3.0R" in msg


def test_format_exit_alert_stopped_out_shows_loss():
    msg = format_exit_alert(
        symbol="AAPL", asset_class="stock", reason="stopped out",
        exit_price=175.0, entry_price=180.0,
    )
    assert "AAPL [STOCK] - STOPPED OUT" in msg
    assert "Exit: 175.00" in msg
    assert "entry was 180.00" in msg
    assert "-2.78%" in msg


def test_format_exit_alert_target_hit_shows_gain():
    msg = format_exit_alert(
        symbol="BTC/USD", asset_class="crypto", reason="target hit",
        exit_price=55000.0, entry_price=50000.0,
    )
    assert "TARGET HIT" in msg
    assert "+10.00%" in msg
