import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.risk.position_sizing import position_size, position_value, exceeds_concentration_cap
from src.risk.portfolio_heat import position_risk_pct, portfolio_heat, would_exceed_heat_cap


def test_position_size_known_values():
    result = position_size(equity=100_000, entry_price=50.0, stop_price=48.0, risk_pct=0.01)
    assert result == pytest.approx(500.0)


def test_position_size_smaller_risk_pct():
    result = position_size(equity=100_000, entry_price=110.0, stop_price=100.0, risk_pct=0.005)
    assert result == pytest.approx(50.0)


def test_position_size_raises_when_stop_at_or_above_entry():
    with pytest.raises(ValueError):
        position_size(equity=100_000, entry_price=50.0, stop_price=50.0, risk_pct=0.01)
    with pytest.raises(ValueError):
        position_size(equity=100_000, entry_price=50.0, stop_price=52.0, risk_pct=0.01)


def test_position_value_known_values():
    assert position_value(shares=500.0, entry_price=50.0) == pytest.approx(25_000.0)


def test_exceeds_concentration_cap_true_case():
    assert exceeds_concentration_cap(position_value_=25_000.0, equity=100_000.0, cap=0.15) is True


def test_exceeds_concentration_cap_false_case():
    assert exceeds_concentration_cap(position_value_=10_000.0, equity=100_000.0, cap=0.15) is False


def test_exceeds_concentration_cap_at_exact_boundary_is_not_exceeding():
    assert exceeds_concentration_cap(position_value_=15_000.0, equity=100_000.0, cap=0.15) is False


def test_position_risk_pct_matches_position_size_inverse():
    shares = position_size(equity=100_000, entry_price=50.0, stop_price=48.0, risk_pct=0.01)
    realized = position_risk_pct(equity=100_000, entry_price=50.0, stop_price=48.0, shares=shares)
    assert realized == pytest.approx(0.01)


def test_position_risk_pct_with_rounded_shares():
    realized = position_risk_pct(equity=100_000, entry_price=50.0, stop_price=48.0, shares=500.0)
    assert realized == pytest.approx(0.01)
    realized_floored = position_risk_pct(equity=100_000, entry_price=50.0, stop_price=48.0, shares=480.0)
    assert realized_floored < 0.01


def test_portfolio_heat_sums_open_positions():
    assert portfolio_heat([0.01, 0.012, 0.008]) == pytest.approx(0.03)


def test_portfolio_heat_empty_is_zero():
    assert portfolio_heat([]) == pytest.approx(0.0)


def test_would_exceed_heat_cap_true_case():
    assert would_exceed_heat_cap(current_heat=0.05, new_position_risk_pct=0.012, heat_cap=0.06) is True


def test_would_exceed_heat_cap_false_case():
    assert would_exceed_heat_cap(current_heat=0.04, new_position_risk_pct=0.01, heat_cap=0.06) is False


def test_would_exceed_heat_cap_exact_boundary_is_not_exceeding():
    assert would_exceed_heat_cap(current_heat=0.05, new_position_risk_pct=0.01, heat_cap=0.06) is False
