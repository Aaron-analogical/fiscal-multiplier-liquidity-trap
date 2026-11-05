"""Run every scenario through Dynare under Octave."""
import json
import os
import subprocess
from pathlib import Path

from scenarios import config_hash, model_hash, scenario_dicts

ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "config" / "scenarios.json"
MODEL = ROOT / "model" / "fiscal.mod"
RAW = ROOT / "results" / "raw"
DEFAULT_OCTAVE = (Path(os.environ.get("LOCALAPPDATA", ""))
                  / "Programs/octave-11.3.0-w64/mingw64/bin/octave-cli.exe")


def solve() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for old in [*RAW.glob("*.csv"), RAW / "manifest.json"]:
        old.unlink(missing_ok=True)
    (RAW / "scenario_list.json").write_text(json.dumps({
        "config_hash": config_hash(CONFIG),
        "model_hash": model_hash(MODEL),
        "scenarios": scenario_dicts(CONFIG),
    }))
    env = dict(os.environ)
    env.setdefault("DYNARE_MATLAB", "C:/dynare/7.2/matlab")
    octave = os.environ.get("OCTAVE_CLI", str(DEFAULT_OCTAVE))
    log = RAW / "solve_output.txt"
    with log.open("w") as handle:
        result = subprocess.run(
            [octave, "--no-gui", "--quiet", "run_scenarios.m"],
            cwd=ROOT / "model", env=env, stdout=handle,
            stderr=subprocess.STDOUT,
        )
    if result.returncode != 0:
        tail = log.read_text(errors="replace").splitlines()[-5:]
        raise SystemExit(f"Model run failed, see {log}.\n" + "\n".join(tail))


if __name__ == "__main__":
    solve()
