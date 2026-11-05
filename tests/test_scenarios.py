import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from scenarios import config_hash, load_scenarios  # noqa: E402

CONFIG = Path(__file__).parents[1] / "config" / "scenarios.json"
CASES = [(0, 1), (1, 1), (1, 16)]


def spending(scenarios):
    return [s for s in scenarios if s.kind == "spending"]


def test_grid_covers_tables():
    found = {(s.financing, s.alpha, s.build_time, s.state)
             for s in spending(load_scenarios(CONFIG)) if s.gamma_n == 0.1}
    for financing in ("lump_sum", "labor_tax", "debt"):
        for alpha, build in CASES:
            for state in ("normal", "trap"):
                assert (financing, alpha, build, state) in found


def test_sensitivity_grid():
    found = {s.gamma_n for s in spending(load_scenarios(CONFIG))
             if s.financing == "debt" and s.alpha == 1
             and s.build_time == 16 and s.state == "trap"}
    assert found == {0.05, 0.1, 0.15, 0.2, 0.25}


def test_each_trap_run_has_baseline():
    scenarios = load_scenarios(CONFIG)
    ids = {s.id: s for s in scenarios}
    for s in spending(scenarios):
        if s.state == "trap":
            assert ids[s.baseline].kind == "baseline"
        else:
            assert s.baseline is None


def test_ids_unique():
    ids = [s.id for s in load_scenarios(CONFIG)]
    assert len(ids) == len(set(ids))


def test_config_hash_changes_when_config_changes(tmp_path):
    path = tmp_path / "config.json"
    data = json.loads(CONFIG.read_text())
    path.write_text(json.dumps(data))
    first = config_hash(path)
    data["eps_g"] = 0.02
    path.write_text(json.dumps(data))
    assert config_hash(path) != first
