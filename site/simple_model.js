// Closed-form multipliers from section 4 of the thesis.
// Mirrors scripts/simple_model.py; tests/simple_model.test.mjs keeps them equal.

export const CALIBRATION = {
  beta: 0.99, theta: 6, gamma: 0.29, a: 1, b: 0.08, kappa: 0.03,
  phi_pi: 1.5, rho: 0.8, p: 0.8, g_bar: 0.2, alpha_bar: 0.23,
  delta: 1, phi_r: 1,
};

const MIN_TRAP_DENOMINATOR = 0.1;
const MAX_MEANINGFUL_MULTIPLIER = 10;
const THETA_TAU = { lump_sum: 0, labor_tax: 1 };

export function multiplier(alpha, financing, state, params = CALIBRATION) {
  if (!(financing in THETA_TAU)) throw new Error(`Unknown financing: ${financing}`);
  const x = params;
  const thetaTau = THETA_TAU[financing] / x.a;
  const markup = (x.theta - 1) / x.theta;
  const thetaG = (x.a / (1 - x.g_bar)) * (x.gamma / (1 - x.gamma)) * markup;
  const thetaK = x.b * (1 + thetaG);
  const deltaTilde = x.delta / (x.alpha_bar * x.g_bar);
  const weight = (1 - x.g_bar) * x.phi_r;
  const invest = alpha * deltaTilde * thetaK - thetaTau;

  if (state === "normal") {
    const rho = x.rho;
    const psi = ((1 - rho) * (1 - x.beta * rho)) / (x.kappa * (x.phi_pi - rho));
    return (1 + psi + weight * invest) / (1 + psi + weight * thetaG);
  }
  if (state === "trap") {
    const p = x.p;
    const psi = ((1 - p) * (1 - x.beta * p)) / (x.kappa * p);
    const denominator = psi - 1 - weight * thetaG;
    if (denominator < MIN_TRAP_DENOMINATOR) return null;
    const value = (psi - 1 - weight * invest) / denominator;
    return Math.abs(value) <= MAX_MEANINGFUL_MULTIPLIER ? value : null;
  }
  throw new Error(`Unknown state: ${state}`);
}
