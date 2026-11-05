import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from multipliers import impact_multiplier, present_value_multiplier  # noqa: E402


def frame(y, g):
    return pd.DataFrame({
        "t": range(len(y)), "y": y, "g": g,
        "y_ss": [1.0] * len(y), "g_ss": [0.2] * len(y),
    })


def test_impact_against_steady_state():
    assert impact_multiplier(frame([1.1, 1.0], [0.3, 0.2])) == pytest.approx(1.0)


def test_impact_against_baseline():
    run = frame([1.3, 1.0], [0.3, 0.2])
    baseline = frame([1.1, 1.0], [0.2, 0.2])
    assert impact_multiplier(run, baseline) == pytest.approx(2.0)


def test_present_value_discounts_later_periods():
    run = frame([1.0, 1.2], [0.3, 0.3])
    result = present_value_multiplier(run, None, rb=1.0)
    assert result == pytest.approx((0 + 0.2 / 2) / (0.1 + 0.1 / 2))


def test_present_value_respects_horizon():
    run = frame([1.1, 9.0], [0.3, 0.3])
    assert present_value_multiplier(run, None, rb=0.0, horizon=1) == pytest.approx(1.0)


def test_zero_spending_change_raises():
    with pytest.raises(ValueError):
        impact_multiplier(frame([1.1, 1.0], [0.2, 0.2]))
