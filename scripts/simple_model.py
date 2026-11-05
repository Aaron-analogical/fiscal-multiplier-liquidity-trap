"""Closed-form multipliers from section 4 of the thesis, equations (43) to (53)."""

CALIBRATION = {
    "beta": 0.99, "theta": 6, "gamma": 0.29, "a": 1, "b": 0.08, "kappa": 0.03,
    "phi_pi": 1.5, "rho": 0.8, "p": 0.8, "g_bar": 0.2, "alpha_bar": 0.23,
    "delta": 1, "phi_r": 1,
}
# Near a zero denominator the trap multiplier explodes or changes sign, so the
# linear solution stops carrying economic meaning. Thesis values stay within 4.
MIN_TRAP_DENOMINATOR = 0.1
MAX_MEANINGFUL_MULTIPLIER = 10
THETA_TAU = {"lump_sum": 0, "labor_tax": 1}


def multiplier(alpha, financing, state, params=CALIBRATION):
    """Return dY/dG, or None when the trap solution has no meaningful value."""
    if financing not in THETA_TAU:
        raise ValueError(f"Unknown financing: {financing}")
    x = params
    theta_tau = THETA_TAU[financing] / x["a"]
    markup = (x["theta"] - 1) / x["theta"]
    theta_g = x["a"] / (1 - x["g_bar"]) * x["gamma"] / (1 - x["gamma"]) * markup
    theta_k = x["b"] * (1 + theta_g)
    delta_tilde = x["delta"] / (x["alpha_bar"] * x["g_bar"])
    weight = (1 - x["g_bar"]) * x["phi_r"]
    invest = alpha * delta_tilde * theta_k - theta_tau

    if state == "normal":
        rho = x["rho"]
        psi = (1 - rho) * (1 - x["beta"] * rho) / (x["kappa"] * (x["phi_pi"] - rho))
        return (1 + psi + weight * invest) / (1 + psi + weight * theta_g)
    if state == "trap":
        p = x["p"]
        psi = (1 - p) * (1 - x["beta"] * p) / (x["kappa"] * p)
        denominator = psi - 1 - weight * theta_g
        if denominator < MIN_TRAP_DENOMINATOR:
            return None
        value = (psi - 1 - weight * invest) / denominator
        return value if abs(value) <= MAX_MEANINGFUL_MULTIPLIER else None
    raise ValueError(f"Unknown state: {state}")
