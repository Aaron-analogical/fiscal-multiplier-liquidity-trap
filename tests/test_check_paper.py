import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from check_paper import compare, expected_english, extract_numbers  # noqa: E402


def test_decimal_comma_equals_decimal_point():
    assert extract_numbers("0,93 et 0.93") == Counter({"0.93": 2})


def test_trailing_zero_is_normalized():
    assert extract_numbers("1,80") == extract_numbers("1.8")


def test_page_numbers_and_integers_are_ignored():
    assert extract_numbers("page 36\n12 trimestres") == Counter()


def test_negative_sign_is_kept_apart():
    assert extract_numbers("-3,18") == Counter({"3.18": 1})


def test_compare_reports_numbers_in_one_version():
    result = compare(Counter({"0.93": 1, "1.8": 1}), Counter({"0.93": 1, "2.2": 1}))
    assert result == {"only_french": ["1.8"], "only_english": ["2.2"]}


def test_corrected_values_map_to_english():
    french = Counter({"0.58": 1, "0.89": 2, "0.176": 1, "0.93": 1})
    assert expected_english(french) == Counter({"0.59": 1, "0.9": 2, "0.172": 1, "0.93": 1})


def test_english_thesis_carries_the_corrections():
    tex = (Path(__file__).parents[1] / "paper" / "thesis_en.tex").read_text(encoding="utf-8")
    for wrong in ("0.176", "0.58", "Theta_r", "Frisch", "Calvo", "(1-g)"):
        assert wrong not in tex, wrong
    assert "Larocque and M. Normandin (2018)" in tex
    assert "minor corrections" in tex
    assert "three printed values" not in tex


PAPER = Path(__file__).parents[1] / "paper"


def test_corrected_french_carries_the_corrections():
    tex = (PAPER / "thesis_fr_corrected.tex").read_text(encoding="utf-8")
    for wrong in ("0,176", "{0,58}", "Theta_r", "Frisch", "Calvo", "New Deal de 1930"):
        assert wrong not in tex, wrong
    assert "Version corrigée" in tex
    assert "reste la version officielle" in tex
    assert "M. Normandin (2018)" in tex


def test_corrected_french_has_the_same_numbers_as_english():
    def numbers(*names):
        return extract_numbers("\n".join((PAPER / n).read_text(encoding="utf-8") for n in names))

    french = numbers("thesis_fr_corrected.tex", "annex_b_nodebt_fr.mod", "annex_b_debt_fr.mod")
    english = numbers("thesis_en.tex", "annex_b_nodebt.mod", "annex_b_debt.mod")
    assert compare(french, english) == {"only_french": [], "only_english": []}


def test_french_figures_exist_for_every_english_figure():
    english = {p.name for p in (PAPER / "figures").glob("figure_*.pdf")}
    assert english == {p.name for p in (PAPER / "figures_fr").glob("figure_*.pdf")}
