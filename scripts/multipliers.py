"""Fiscal multipliers from simulated paths, thesis equations (55) and (56)."""
import pandas as pd

RB = 1 / 0.99 - 1


def _changes(run: pd.DataFrame, baseline: pd.DataFrame | None):
    if baseline is None:
        return run["y"] - run["y_ss"], run["g"] - run["g_ss"]
    return run["y"] - baseline["y"], run["g"] - baseline["g"]


def impact_multiplier(run: pd.DataFrame, baseline: pd.DataFrame | None = None) -> float:
    dy, dg = _changes(run, baseline)
    if dg.iloc[0] == 0:
        raise ValueError("Government spending does not change on impact")
    return float(dy.iloc[0] / dg.iloc[0])


def present_value_multiplier(run: pd.DataFrame, baseline: pd.DataFrame | None = None,
                             rb: float = RB, horizon: int = 500) -> float:
    dy, dg = _changes(run, baseline)
    discount = (1 + rb) ** -run["t"]
    keep = run["t"] < horizon
    denominator = (discount * dg)[keep].sum()
    if denominator == 0:
        raise ValueError("Government spending does not change")
    return float((discount * dy)[keep].sum() / denominator)
