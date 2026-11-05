import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from simple_model import CALIBRATION, multiplier  # noqa: E402

THESIS_VALUES = [
    ("lump_sum", "normal", 0, 0.90),
    ("lump_sum", "normal", 1, 1.49),
    ("lump_sum", "trap", 0, 1.87),
    ("lump_sum", "trap", 1, -3.18),
    ("labor_tax", "normal", 0, 0.66),
    ("labor_tax", "normal", 1, 1.25),
    ("labor_tax", "trap", 0, 3.9),
    ("labor_tax", "trap", 1, -1.15),
]


@pytest.mark.parametrize("financing,state,alpha,expected", THESIS_VALUES)
def test_thesis_values(financing, state, alpha, expected):
    assert multiplier(alpha, financing, state) == pytest.approx(expected, abs=0.01)


@pytest.mark.parametrize("financing,alpha", [("lump_sum", 0.172), ("labor_tax", 0.575)])
@pytest.mark.parametrize("state", ["normal", "trap"])
def test_break_even(financing, alpha, state):
    assert multiplier(alpha, financing, state) == pytest.approx(1, abs=0.05)


@pytest.mark.parametrize("alpha", [0, 0.25, 0.5, 0.75, 1])
def test_proposition_1_normal_times(alpha):
    assert multiplier(alpha, "labor_tax", "normal") < multiplier(alpha, "lump_sum", "normal")


@pytest.mark.parametrize("alpha", [0, 0.25, 0.5, 0.75, 1])
def test_proposition_2_trap(alpha):
    assert multiplier(alpha, "labor_tax", "trap") > multiplier(alpha, "lump_sum", "trap")


def test_singular_returns_none():
    params = {**CALIBRATION, "p": 0.9}
    assert multiplier(0, "lump_sum", "trap", params) is None


def test_normal_times_ignores_trap_persistence():
    params = {**CALIBRATION, "p": 0.9}
    assert multiplier(0, "lump_sum", "normal", params) == multiplier(0, "lump_sum", "normal")


def test_unknown_financing_is_rejected():
    with pytest.raises(ValueError):
        multiplier(0, "debt", "normal")


@pytest.mark.parametrize("financing,alpha", [("lump_sum", 1), ("labor_tax", 0)])
def test_near_singular_slider_position_returns_none(financing, alpha):
    params = {**CALIBRATION, "p": 0.82}
    assert multiplier(alpha, financing, "trap", params) is None


def test_no_slider_position_gives_a_huge_multiplier():
    for p_step in range(50, 91):
        for kappa_step in range(2, 13):
            params = {**CALIBRATION, "p": p_step / 100, "kappa": kappa_step * 0.005}
            for alpha_step in range(0, 101):
                for financing in ("lump_sum", "labor_tax"):
                    value = multiplier(alpha_step / 100, financing, "trap", params)
                    assert value is None or abs(value) <= 10
