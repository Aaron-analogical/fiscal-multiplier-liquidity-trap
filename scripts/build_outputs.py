"""Rebuild thesis tables and figures from model output."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from multipliers import RB, impact_multiplier, present_value_multiplier  # noqa: E402
from simple_model import multiplier  # noqa: E402

ROOT = Path(__file__).parents[1]
RAW = ROOT / "results" / "raw"
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
PAPER_FIGURES = ROOT / "paper" / "figures"
BLUE, ORANGE = "#2a78d6", "#eb6834"
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
HORIZON = 51
CASES = [(0, 1), (1, 1), (1, 16)]
CASE_LABELS = ["α=0", "α=1, q=1", "α=1, q=16"]
LABELS = {"lump_sum": "lump-sum tax", "labor_tax": "labor tax", "debt": "debt"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.titlecolor": INK, "axes.grid": True, "grid.color": GRID,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150,
    "lines.linewidth": 2,
})


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{name}.csv")


def stem(financing: str, alpha: int, build: int, gamma: int = 10) -> str:
    suffix = f"_g{gamma}" if financing == "debt" else ""
    return f"{financing}_a{alpha}_q{build}{suffix}"


def multipliers_for(financing, alpha, build, gamma=10) -> dict:
    name = stem(financing, alpha, build, gamma)
    normal = load(f"{name}_normal")
    trap, baseline = load(f"{name}_trap"), load(f"{name}_baseline")
    return {
        "impact_normal": impact_multiplier(normal),
        "impact_trap": impact_multiplier(trap, baseline),
        "present_value_normal": present_value_multiplier(normal),
        "present_value_trap": present_value_multiplier(trap, baseline),
    }


def write_tables() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    for table, financing in [("5_1", "lump_sum"), ("5_2", "labor_tax"), ("6_1", "debt")]:
        rows = {label: multipliers_for(financing, a, q)
                for label, (a, q) in zip(CASE_LABELS, CASES)}
        pd.DataFrame(rows).round(3).to_csv(TABLES / f"table_{table}.csv")
    rows = []
    for gamma in (5, 10, 15, 20, 25):
        name = stem("debt", 1, 16, gamma)
        trap, baseline = load(f"{name}_trap"), load(f"{name}_baseline")
        rows.append({"gamma_n": gamma / 100,
                     "impact_trap": impact_multiplier(trap, baseline),
                     "present_value_trap": present_value_multiplier(trap, baseline)})
    pd.DataFrame(rows).round(3).to_csv(TABLES / "table_6_2.csv", index=False)


def save(fig, name: str, title: str) -> None:
    """Save a titled PNG for the repo and an untitled PDF for the thesis."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(PAPER_FIGURES / f"{name}.pdf", bbox_inches="tight")
    fig.suptitle(title, x=0.07, ha="left", fontsize=11)
    fig.savefig(FIGURES / f"{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def label_line(ax, x, y, text) -> None:
    ax.annotate(text, (x, y), xytext=(4, 0), textcoords="offset points",
                color=INK, va="center", fontsize=9)


def simple_figure(financing: str, number: str) -> None:
    alphas = np.linspace(0, 1, 101)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for state, color, name in [("normal", BLUE, "Normal times"),
                               ("trap", ORANGE, "Liquidity trap")]:
        values = [multiplier(a, financing, state) for a in alphas]
        ax.plot(alphas * 100, values, color=color, label=name)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set_xlabel("Share of public spending going to investment, α (%)")
    ax.set_ylabel("Multiplier")
    ax.legend(frameon=False)
    save(fig, f"figure_{number.replace('.', '_')}",
         f"Figure {number}: multiplier by investment share, {LABELS[financing]} financing")


def real_rate(run: pd.DataFrame) -> pd.Series:
    """Nominal rate less current inflation, the measure plotted in the thesis."""
    return run.ii - run.pie


def impulse_figure(number, financing, alpha, build) -> None:
    name = stem(financing, alpha, build)
    normal = load(f"{name}_normal").head(HORIZON)
    trap = load(f"{name}_trap").head(HORIZON)
    base = load(f"{name}_baseline").head(HORIZON)
    panels = [
        ("GDP", "% of steady state",
         100 * (normal.y - normal.y_ss) / normal.y_ss, 100 * (trap.y - base.y) / trap.y_ss),
        ("Real interest rate", "percentage points, annual",
         400 * (real_rate(normal) - RB), 400 * (real_rate(trap) - real_rate(base))),
        ("Nominal interest rate", "%, annual", 400 * normal.ii, 400 * trap.ii),
    ]
    if financing != "lump_sum":
        panels.append(("Labor tax rate", "%", 100 * normal.tau, 100 * trap.tau))
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharex=True)
    for ax, (title, unit, first, second) in zip(axes.flat, panels):
        ax.plot(normal.t, first, color=BLUE, label="Normal times")
        ax.plot(trap.t, second, color=ORANGE, label="Liquidity trap")
        ax.set_title(title, loc="left", fontsize=10)
        ax.set_ylabel(unit)
    axes.flat[0].legend(frameon=False)
    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("Quarters")
    case = f"α={alpha}" if alpha == 0 else f"α={alpha}, q={build}"
    fig.tight_layout()
    save(fig, f"figure_{number.replace('.', '_')}",
         f"Figure {number}: response to a spending shock, {case}, "
         f"{LABELS[financing]} financing")


def tax_path_figure() -> None:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for color, gamma in zip(RAMP, (5, 10, 15, 20, 25)):
        run = load(f"debt_a1_q16_g{gamma}_trap").head(HORIZON)
        ax.plot(run.t, 100 * run.tau, color=color, label=f"γₙ = {gamma / 100:g}")
    ax.set_xlabel("Quarters")
    ax.set_ylabel("Labor tax rate (%)")
    ax.legend(frameon=False)
    save(fig, "figure_6_1", "Figure 6.1: labor tax path in a liquidity trap, "
         "by tax response to debt")


def headline_figure() -> None:
    """The README chart: the ranking from the simple model reverses."""
    full = {f: multipliers_for(f, 0, 1)["present_value_trap"]
            for f in ("lump_sum", "labor_tax")}
    simple = {f: multiplier(0, f, "trap") for f in ("lump_sum", "labor_tax")}
    fig, ax = plt.subplots(figsize=(7, 3.6))
    groups = np.arange(2)
    width = 0.34
    series = [("lump_sum", BLUE, "Lump-sum tax"), ("labor_tax", ORANGE, "Labor tax")]
    for offset, (financing, color, name) in zip((-1, 1), series):
        values = [simple[financing], full[financing]]
        bars = ax.bar(groups + offset * (width / 2 + 0.01), values, width,
                      color=color, label=name)
        ax.bar_label(bars, fmt="%.2f", padding=3, color=INK)
    ax.set_xticks(groups, ["Simple model", "Full dynamic model"])
    ax.set_ylabel("Multiplier")
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    ax.set_ylim(0, 4.5)
    ax.legend(frameon=False)
    save(fig, "headline", "In a liquidity trap, the better way to finance spending flips")


def build_all() -> None:
    write_tables()
    simple_figure("lump_sum", "4.1")
    simple_figure("labor_tax", "4.2")
    for number, financing, alpha, build in [
        ("5.1", "lump_sum", 0, 1), ("5.2", "labor_tax", 0, 1),
        ("5.3", "lump_sum", 1, 1), ("5.4", "labor_tax", 1, 1),
        ("5.5", "lump_sum", 1, 16), ("5.6", "labor_tax", 1, 16),
    ]:
        impulse_figure(number, financing, alpha, build)
    tax_path_figure()
    headline_figure()


if __name__ == "__main__":
    build_all()
    print(json.dumps({"figures": len(list(FIGURES.glob("*.png"))),
                      "tables": len(list(TABLES.glob("*.csv")))}))
