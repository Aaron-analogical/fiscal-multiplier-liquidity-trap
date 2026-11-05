"""Write the data files behind the interactive page."""
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from multipliers import RB, impact_multiplier, present_value_multiplier
from scenarios import load_scenarios
from simple_model import CALIBRATION, multiplier

ROOT = Path(__file__).parents[1]
RAW = ROOT / "results" / "raw"
SITE_DATA = ROOT / "site" / "data"
QUARTERS = 51


def _rounded(values) -> list[float]:
    return [round(float(v), 4) for v in values]


def _path(run: pd.DataFrame, baseline: pd.DataFrame | None) -> dict:
    run = run.head(QUARTERS)
    real = run.ii - run.pie
    if baseline is None:
        gdp, real_change = 100 * (run.y - run.y_ss) / run.y_ss, 400 * (real - RB)
    else:
        base = baseline.head(QUARTERS)
        gdp = 100 * (run.y - base.y) / run.y_ss
        real_change = 400 * (real - (base.ii - base.pie))
    return {"gdp": _rounded(gdp), "real_rate": _rounded(real_change),
            "nominal_rate": _rounded(400 * run.ii), "tax": _rounded(100 * run.tau)}


def full_model_rows() -> list[dict]:
    rows = []
    for s in load_scenarios(ROOT / "config" / "scenarios.json"):
        if s.kind != "spending":
            continue
        run = pd.read_csv(RAW / f"{s.id}.csv")
        baseline = pd.read_csv(RAW / f"{s.baseline}.csv") if s.baseline else None
        fields = asdict(s)
        rows.append({
            **{k: fields[k] for k in ("financing", "alpha", "build_time", "gamma_n", "state")},
            "impact": round(impact_multiplier(run, baseline), 4),
            "present_value": round(present_value_multiplier(run, baseline), 4),
            "source": "thesis",
            "path": _path(run, baseline),
        })
    return rows


def build_fixture() -> list[dict]:
    rows = []
    for financing in ("lump_sum", "labor_tax"):
        for state in ("normal", "trap"):
            for alpha in (0, 0.25, 0.5, 0.75, 1):
                for p in (0.5, 0.7, 0.8, 0.82, 0.9):
                    for kappa in (0.01, 0.03, 0.06):
                        params = {**CALIBRATION, "p": p, "kappa": kappa}
                        rows.append({
                            "alpha": alpha, "financing": financing, "state": state,
                            "params": params,
                            "expected": multiplier(alpha, financing, state, params),
                        })
    return rows


def build_site_data() -> None:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    (SITE_DATA / "full_model.json").write_text(
        json.dumps({"scenarios": full_model_rows()}, separators=(",", ":")))
    (SITE_DATA / "simple_fixture.json").write_text(json.dumps(build_fixture()))


if __name__ == "__main__":
    build_site_data()
