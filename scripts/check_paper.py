"""Check that the English thesis carries the same numbers as the French one."""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[1]
DECIMAL = re.compile(r"(?<![\d.,])\d+[.,]\d+(?!\d)")
# Chart axis ticks and section numbers in the French PDF, reviewed by hand.
NOT_CONTENT = {"0", "0.4", "0.7", "0.9", "1", "1.4", "2", "2.1", "2.5", "3", "3.1", "3.2",
               "3.3", "3.5", "4", "4.3", "4.4", "4.5", "5"}


def extract_numbers(text: str) -> Counter:
    numbers = (m.replace(",", ".") for m in DECIMAL.findall(text))
    return Counter(n.rstrip("0").rstrip(".") for n in numbers)


def compare(french: Counter, english: Counter) -> dict:
    return {"only_french": sorted(set(french) - set(english)),
            "only_english": sorted(set(english) - set(french))}


def main() -> int:
    french = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(ROOT / "paper/thesis_fr.pdf"), "-"],
        capture_output=True, check=True).stdout.decode("utf-8", "replace")
    english = "\n".join(
        (ROOT / "paper" / name).read_text(encoding="utf-8")
        for name in ("thesis_en.tex", "annex_b_nodebt.mod", "annex_b_debt.mod"))
    found = extract_numbers(french)
    for number in NOT_CONTENT:
        del found[number]
    result = compare(found, extract_numbers(english))
    print(result)
    return 1 if result["only_french"] else 0


if __name__ == "__main__":
    sys.exit(main())
