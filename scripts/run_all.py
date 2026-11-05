"""Single entry point: solve the model, rebuild outputs, validate them."""
import sys
from pathlib import Path

from build_outputs import build_all
from solve import CONFIG, MODEL, RAW, ROOT, solve
from validate import validate, write_report


def main() -> int:
    if "--skip-solve" not in sys.argv:
        solve()
    report = validate(RAW, CONFIG, MODEL, ROOT / "config" / "thesis_targets.json")
    write_report(report, ROOT / "results")
    if report["status"] == "stale":
        print(f"Validation refused: {report['reason']}", file=sys.stderr)
        return 1
    build_all()
    print(f"{report['status']}: {report['matched']} of {report['compared']} "
          "checks agree. See results/validation.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
