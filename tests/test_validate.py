import json
import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from scenarios import config_hash, load_scenarios, model_hash  # noqa: E402
from validate import matches, validate  # noqa: E402

CONFIG = ROOT / "config" / "scenarios.json"
MODEL = ROOT / "model" / "fiscal.mod"
TARGETS = ROOT / "config" / "thesis_targets.json"


@pytest.fixture
def raw(tmp_path):
    """Synthetic run: output rises by 1.0 for every unit of spending."""
    scenarios = {}
    for s in load_scenarios(CONFIG):
        rows = pd.DataFrame({
            "t": range(3), "y": [1.0] * 3, "g": [0.2] * 3,
            "y_ss": [1.0] * 3, "g_ss": [0.2] * 3,
        })
        if s.kind == "spending":
            rows["y"] = [1.1, 1.05, 1.0]
            rows["g"] = [0.3, 0.25, 0.2]
        rows.to_csv(tmp_path / f"{s.id}.csv", index=False)
        scenarios[s.id] = {
            "converged": True,
            "zlb_quarters": 12 if s.kind == "baseline" else 0,
        }
    manifest = {"config_hash": config_hash(CONFIG), "model_hash": model_hash(MODEL),
                "dynare_version": "test", "scenarios": scenarios}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    return tmp_path


def run(raw_dir):
    return validate(raw_dir, CONFIG, MODEL, TARGETS)


def edit_manifest(raw_dir, change):
    path = raw_dir / "manifest.json"
    manifest = json.loads(path.read_text())
    change(manifest)
    path.write_text(json.dumps(manifest))


def test_stale_manifest_is_refused(raw):
    edit_manifest(raw, lambda m: m.update(model_hash="old"))
    assert run(raw)["status"] == "stale"


def test_missing_manifest_is_refused(tmp_path):
    assert run(tmp_path)["status"] == "stale"


def test_incomplete_manifest_fails(raw):
    def drop_one(manifest):
        manifest["scenarios"].popitem()
    edit_manifest(raw, drop_one)
    assert run(raw)["status"] == "stale"


def test_unconverged_run_fails(raw):
    def fail_one(manifest):
        next(iter(manifest["scenarios"].values()))["converged"] = False
    edit_manifest(raw, fail_one)
    assert run(raw)["status"] == "stale"


def test_trap_length_flagged(raw):
    def shorten(manifest):
        for name, entry in manifest["scenarios"].items():
            if name.endswith("baseline"):
                entry["zlb_quarters"] = 9
                break
    edit_manifest(raw, shorten)
    report = run(raw)
    rows = [r for r in report["rows"] if r["check"] == "trap length"]
    assert any(not r["match"] for r in rows)
    assert report["status"] == "mismatch"


def test_rounding_rule():
    assert matches(0.931, 0.93)
    assert matches(0.935, 0.93)
    assert not matches(0.94, 0.93)


def test_three_decimal_values_use_tighter_rule():
    assert matches(0.1716, 0.172, tolerance=0.00051)
    assert not matches(0.1716, 0.176, tolerance=0.00051)


def test_report_lists_table_rows(raw):
    labels = {r["table"] for r in run(raw)["rows"]}
    assert {"5.1", "5.2", "6.1", "6.2"} <= labels
