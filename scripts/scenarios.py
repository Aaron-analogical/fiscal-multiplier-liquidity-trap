"""Expand config/scenarios.json into the list of model runs."""
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    id: str
    financing: str
    alpha: float
    build_time: int
    gamma_n: float
    state: str
    kind: str
    baseline: str | None
    eps_zeta: float
    eps_g: float


def _make(config, financing, alpha, build_time, gamma_n, state):
    stem = f"{financing}_a{alpha:g}_q{build_time}"
    if financing == "debt":
        stem += f"_g{round(gamma_n * 100)}"
    baseline_id = f"{stem}_baseline"
    spending = Scenario(
        f"{stem}_{state}", financing, alpha, build_time, gamma_n, state,
        "spending", baseline_id if state == "trap" else None,
        config["eps_zeta"] if state == "trap" else 0.0, config["eps_g"],
    )
    if state == "normal":
        return [spending]
    baseline = Scenario(
        baseline_id, financing, alpha, build_time, gamma_n, "trap",
        "baseline", None, config["eps_zeta"], 0.0,
    )
    return [spending, baseline]


def load_scenarios(path) -> list[Scenario]:
    config = json.loads(Path(path).read_text())
    gamma_n = config["default_gamma_n"]
    scenarios = []
    for financing in config["financing"]:
        for case in config["cases"]:
            for state in ("normal", "trap"):
                scenarios += _make(config, financing, case["alpha"],
                                   case["build_time"], gamma_n, state)
    extra = config["sensitivity"]
    for value in extra["gamma_n"]:
        scenarios += _make(config, extra["financing"], extra["alpha"],
                           extra["build_time"], value, extra["state"])
    return scenarios


def _hash(path) -> str:
    text = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(text).hexdigest()


def config_hash(path) -> str:
    return _hash(path)


def model_hash(path) -> str:
    return _hash(path)


def scenario_dicts(path) -> list[dict]:
    return [asdict(s) for s in load_scenarios(path)]
