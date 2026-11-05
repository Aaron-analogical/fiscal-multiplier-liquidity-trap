import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
DOCS = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
LINK = re.compile(r"\]\((?!https?://|#)([^)#]+)")
BANNED = re.compile(r"(\.docx|\.xlsx|\.tmp|~\$.*)$", re.IGNORECASE)


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: p.name)
def test_relative_links_resolve(doc):
    for target in LINK.findall(doc.read_text(encoding="utf-8")):
        assert (doc.parent / target).exists(), f"{doc.name}: {target}"


def test_no_scratch_files_in_repo():
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.splitlines()
    assert [name for name in tracked if BANNED.search(name)] == []


def test_readme_reports_validation_truthfully():
    report = json.loads((ROOT / "results" / "validation.json").read_text())
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"{report['matched']} of {report['compared']}" in readme
    if report["status"] != "pass":
        assert "results/validation.md" in readme
