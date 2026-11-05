import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site_data import build_fixture, full_model_rows  # noqa: E402
from simple_model import CALIBRATION  # noqa: E402


@pytest.fixture(scope="module")
def rows():
    return full_model_rows()


def find(rows, **wanted):
    return next(r for r in rows if all(r[k] == v for k, v in wanted.items()))


def test_every_thesis_grid_point_is_marked_thesis(rows):
    spending = [r for r in rows]
    assert len(spending) == 22
    assert {r["source"] for r in spending} == {"thesis"}


def test_numbers_equal_validated_tables(rows):
    row = find(rows, financing="labor_tax", alpha=1, build_time=16, state="trap")
    assert row["impact"] == pytest.approx(0.917, abs=0.001)
    assert row["present_value"] == pytest.approx(2.109, abs=0.001)


def test_sensitivity_rows_exist(rows):
    row = find(rows, financing="debt", gamma_n=0.25, state="trap", alpha=1, build_time=16)
    assert row["present_value"] == pytest.approx(2.15, abs=0.001)


def test_paths_cover_fifty_quarters(rows):
    path = rows[0]["path"]
    assert set(path) == {"gdp", "real_rate", "nominal_rate", "tax"}
    assert all(len(values) == 51 for values in path.values())


def test_trap_paths_are_relative_to_baseline(rows):
    row = find(rows, financing="lump_sum", alpha=0, state="trap")
    assert row["path"]["gdp"][0] == pytest.approx(row["impact"], abs=0.02)
    assert row["path"]["real_rate"][0] == pytest.approx(-0.31, abs=0.01)


def test_fixture_includes_defaults_and_null_rows():
    fixture = build_fixture()
    assert any(r["expected"] is None for r in fixture)
    default = next(r for r in fixture if r["alpha"] == 0 and r["params"] == CALIBRATION
                   and r["financing"] == "lump_sum" and r["state"] == "trap")
    assert default["expected"] == pytest.approx(1.8662, abs=0.001)


def test_committed_data_is_valid_json():
    data = json.loads((ROOT / "site" / "data" / "full_model.json").read_text())
    assert len(data["scenarios"]) == 22
