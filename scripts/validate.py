"""Compare regenerated results with the numbers printed in the thesis."""
import json
from pathlib import Path

import pandas as pd

from multipliers import impact_multiplier, present_value_multiplier
from scenarios import config_hash, load_scenarios, model_hash
from simple_model import multiplier

TRAP_QUARTERS = 12
PRINTED_ROUNDING = 0.0051
THREE_DECIMALS = 0.00051
MEASURES = {"impact": impact_multiplier, "present_value": present_value_multiplier}


def matches(computed: float, thesis: float, tolerance: float = PRINTED_ROUNDING) -> bool:
    """True when both agree at the precision printed in the thesis."""
    return abs(computed - thesis) <= tolerance


def _stale(reason: str) -> dict:
    return {"status": "stale", "reason": reason, "rows": []}


def _check_manifest(raw_dir, config, model, scenarios):
    path = Path(raw_dir) / "manifest.json"
    if not path.exists():
        return None, "No manifest: the model has not been run."
    manifest = json.loads(path.read_text())
    if manifest["config_hash"] != config_hash(config):
        return None, "Scenario config changed since the last model run."
    if manifest["model_hash"] != model_hash(model):
        return None, "Model file changed since the last model run."
    runs = manifest["scenarios"]
    missing = [s.id for s in scenarios if s.id not in runs]
    if missing:
        return None, f"Missing scenario results: {missing[0]}"
    failed = [name for name, entry in runs.items() if not entry["converged"]]
    if failed:
        return None, f"Scenario did not converge: {failed[0]}"
    return manifest, None


def _row(table, label, thesis, computed, notes, check="value",
         tolerance=PRINTED_ROUNDING):
    return {"table": table, "check": check, "label": label, "thesis": thesis,
            "computed": computed, "match": matches(computed, thesis, tolerance),
            "note": notes.get(label, "")}


def validate(raw_dir, config, model, targets_path) -> dict:
    scenarios = load_scenarios(config)
    manifest, reason = _check_manifest(raw_dir, config, model, scenarios)
    if reason:
        return _stale(reason)

    targets = json.loads(Path(targets_path).read_text())
    notes = targets["notes"]
    index = {(s.financing, s.alpha, s.build_time, s.gamma_n, s.state): s
             for s in scenarios if s.kind == "spending"}
    frames = {}

    def frame(name):
        if name not in frames:
            frames[name] = pd.read_csv(Path(raw_dir) / f"{name}.csv")
        return frames[name]

    def value(measure, financing, alpha, build, gamma_n, state):
        s = index[(financing, alpha, build, gamma_n, state)]
        baseline = frame(s.baseline) if s.baseline else None
        return MEASURES[measure](frame(s.id), baseline)

    rows = []
    default_gamma = 0.1
    for table, spec in targets["tables"].items():
        for measure in MEASURES:
            for state, printed in spec[measure].items():
                for column, thesis in zip(targets["columns"], printed):
                    alpha, build = column["alpha"], column["build_time"]
                    label = f"Table {table} {measure} {state} alpha={alpha} q={build}"
                    computed = value(measure, spec["financing"], alpha, build,
                                     default_gamma, state)
                    rows.append(_row(table, label, thesis, computed, notes))

    extra = targets["sensitivity"]
    for entry in extra["rows"]:
        for measure in MEASURES:
            label = f"Table {extra['table']} {measure} gamma_n={entry['gamma_n']}"
            computed = value(measure, "debt", 1, 16, entry["gamma_n"], "trap")
            rows.append(_row(extra["table"], label, entry[measure], computed, notes))

    for entry in targets["simple_model"]:
        label = (f"Simple model {entry['financing']} {entry['state']} "
                 f"alpha={entry['alpha']}")
        computed = multiplier(entry["alpha"], entry["financing"], entry["state"])
        rows.append(_row("4.4", label, entry["value"], computed, notes))

    for entry in targets["break_even"]:
        start = multiplier(0, entry["financing"], "normal")
        end = multiplier(1, entry["financing"], "normal")
        label = f"Break-even {entry['financing']}"
        rows.append(_row("4.4", label, entry["alpha"], (1 - start) / (end - start), notes,
                         tolerance=THREE_DECIMALS))

    for s in scenarios:
        if s.kind == "baseline":
            rows.append(_row("5", f"Trap length {s.id}", TRAP_QUARTERS,
                             manifest["scenarios"][s.id]["zlb_quarters"], notes,
                             check="trap length"))

    return {
        "status": "pass" if all(r["match"] for r in rows) else "mismatch",
        "dynare_version": manifest["dynare_version"],
        "compared": len(rows),
        "matched": sum(r["match"] for r in rows),
        "rows": rows,
    }


def write_report(report: dict, out_dir) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "validation.json").write_text(json.dumps(report, indent=2))
    lines = ["# Validation report", ""]
    if report["status"] == "stale":
        lines.append(f"Status: stale. {report['reason']}")
    else:
        lines += [
            f"Status: {report['status']}. {report['matched']} of "
            f"{report['compared']} checks are within 0.005 of the value printed in "
            f"the thesis (0.0005 for the three-decimal break-evens), using Dynare "
            f"{report['dynare_version']} under GNU Octave.",
            "",
        ]
        different = [r for r in report["rows"] if not r["match"]]
        if different:
            lines += ["## Differences", "",
                      "| Check | Thesis | This run | Explanation |",
                      "|---|---|---|---|"]
            for r in different:
                lines.append(f"| {r['label']} | {r['thesis']} | "
                             f"{r['computed']:.4f} | {r['note'] or 'Unexplained'} |")
            lines.append("")
        lines += ["## All checks", "", "| Check | Thesis | This run | Agrees |",
                  "|---|---|---|---|"]
        for r in report["rows"]:
            lines.append(f"| {r['label']} | {r['thesis']} | {r['computed']:.3f} | "
                         f"{'yes' if r['match'] else 'no'} |")
    (out / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
