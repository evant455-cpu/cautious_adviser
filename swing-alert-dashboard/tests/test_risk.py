from src.config import PORTFOLIO_HEAT_CAP_PCT, RISK_PER_TRADE_PCT
from src.risk.portfolio_heat import OpenRisk, aggregate_btc_exposure, can_add_position, is_btc_correlated
from src.risk.position_sizing import shares_for_risk


def test_shares_for_risk_one_percent_rule():
    shares = shares_for_risk(
        account_equity=100_000,
        entry_price=50.0,
        stop_price=48.0,
        risk_pct=RISK_PER_TRADE_PCT,
    )
    assert shares == 500


def test_shares_for_risk_zero_when_stop_above_entry():
    assert shares_for_risk(100_000, 50.0, 52.0) == 0


def test_portfolio_heat_cap():
    positions = [
        OpenRisk("SPY", 0.02),
        OpenRisk("QQQ", 0.02),
    ]
    assert can_add_position(positions, new_risk_pct=0.01)
    assert not can_add_position(positions, new_risk_pct=0.03)


def test_btc_correlation():
    assert is_btc_correlated("BTC/USD") is True
    assert is_btc_correlated("SPY") is False


def test_aggregate_btc_exposure():
    positions = [
        OpenRisk("BTC/USD", 0.01),
        OpenRisk("ETH/USD", 0.01),
        OpenRisk("SPY", 0.01),
    ]
    assert aggregate_btc_exposure(positions) == 0.02
    assert aggregate_btc_exposure(positions) <= PORTFOLIO_HEAT_CAP_PCT
