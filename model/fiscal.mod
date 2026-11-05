// New Keynesian model of government spending with an occasionally binding
// zero lower bound. Merges the two listings in Annex B of the thesis.
//
// Compile-time options, set by model/run_scenarios.m:
//   DEBT       0 = balanced budget, 1 = debt financing with a labor-tax rule
//   ETA        balanced budget only: 1 = lump-sum tax, 0 = labor tax
//   ALPHA      share of the stimulus spent on public investment
//   BUILD      time-to-build in quarters (q in equation 19)
//   GAMMA_N    response of the labor tax to debt
//   EPS_ZETA   size of the liquidity-preference shock
//   EPS_G      size of the government-spending shock

var y g tau ii pie T y_n c Uc Un Q gi k n mc w zeta
@#if DEBT
    d
@#endif
;

varexo eps_zeta epsg;

parameters eta Beta PSI sigma rb Theta delta gamma gamma_n a b phipi rho
    rho_zeta rho_n gbar alphabar phi_y rho_R alpha
    gi_ss T_ss Q_ss ii_ss mc_ss pie_ss g_ss n_ss k_ss y_ss y_n_ss Uc_ss Un_ss
    c_ss w_ss tau_ss d_ss;

// Calibration (Table 4.1 and section 5 of the thesis)
eta = @{ETA};
alpha = @{ALPHA};
gamma_n = @{GAMMA_N};
Beta = 0.99;
PSI = 5/0.03;
sigma = 1;
delta = 0.025;
gamma = 0.29;
a = 1;
b = 0.08;
phipi = 1.5;
phi_y = 0.05;
rho_R = 0;
rho = 0.8;
rho_zeta = 0.95;
rho_n = 0.5;
gbar = 0.2;
alphabar = 0.23;
Theta = 6;
rb = 1/Beta - 1;

// Steady state
tau_ss = 0;
mc_ss = (Theta-1)/Theta;
n_ss = ((1-gamma)/gamma*(1-gbar)/a*(1/mc_ss)*1/(1-tau_ss)+1)^(-1);
c_ss = ((1-gbar)*n_ss^a*(alphabar*gbar)^b*(delta*(1-gbar))^(-b))^(1/(1-b));
Uc_ss = gamma*c_ss^(gamma*(1-sigma)-1)*(1-n_ss)^((1-gamma)*(1-sigma));
Un_ss = -(1-gamma)*c_ss^(gamma*(1-sigma))*(1-n_ss)^((1-gamma)*(1-sigma)-1);
Q_ss = 1;
k_ss = 1/delta*alphabar*gbar/(1-gbar)*c_ss;
g_ss = delta*k_ss/alphabar;
T_ss = g_ss;
y_ss = c_ss + g_ss;
y_n_ss = a*y_ss/n_ss;
w_ss = (1-gamma)/(1-n_ss)*c_ss/gamma*1/(1-tau_ss);
pie_ss = 0;
ii_ss = rb;
gi_ss = alphabar*g_ss;
d_ss = tau_ss*w_ss*n_ss/ii_ss;

model;

// Marginal utilities, marginal product of labor, stochastic discount factor
Uc = gamma*c^(gamma*(1-sigma)-1)*(1-n)^((1-gamma)*(1-sigma));
Un = -(1-gamma)*c^(gamma*(1-sigma))*(1-n)^((1-gamma)*(1-sigma)-1);
y_n = a*y/n;
Q = Uc/Uc(-1);

// Resource constraint, production
y = c + g + PSI/2*pie^2*y;
y = n^a*k^b;

// Labor supply, Euler equation
w = -Un/Uc*1/(1-tau);
0 = zeta/Uc + (1+ii)/(1+pie(+1))*Beta*Q(+1) - 1;

// Firms: price setting and marginal cost
mc = (Theta-1)/Theta + PSI/Theta*pie*(1+pie)
     - PSI/Theta*Q(+1)*y(+1)/y*pie(+1)*(1+pie(+1));
mc = w/y_n;

// Public capital accumulation and public investment
@#if BUILD == 0
k = (1-delta)*k(-1) + gi;
@#else
k = (1-delta)*k(-1) + gi(-@{BUILD});
@#endif
gi = gi_ss + alpha*(g-g_ss);

// Taylor rule with zero lower bound
ii = max(0, (1+ii_ss)*((1+ii(-1))/(1+ii_ss))^rho_R
            *((1+pie)^phipi*(y/y_ss)^phi_y)^(1-rho_R) - 1);

// Fiscal policy
@#if DEBT
g + ii*d(-1) = T + tau*w*n + d - d(-1);
T = T_ss;
tau = (1-rho_n)*tau_ss + rho_n*tau(-1) + (1-rho_n)*gamma_n*(d(-1)/y - d_ss/y_ss);
@#else
g = T + tau*(w*n);
T = eta*g + (1-eta)*T_ss;
@#endif

// Exogenous processes
(g-g_ss)/y_ss = rho*(g(-1)-g_ss)/y_ss + epsg;
zeta = rho_zeta*zeta(-1) + eps_zeta;

end;

initval;
c = c_ss; T = T_ss; k = k_ss; y = y_ss; n = n_ss; ii = ii_ss; w = w_ss;
tau = tau_ss; pie = pie_ss; mc = mc_ss; g = g_ss; gi = gi_ss; Uc = Uc_ss;
Un = Un_ss; y_n = y_n_ss; Q = Q_ss; zeta = 0;
@#if DEBT
d = d_ss;
@#endif
end;

steady;

shocks;
var eps_zeta;
periods 1;
values @{EPS_ZETA};
var epsg;
periods 1;
values @{EPS_G};
end;

perfect_foresight_setup(periods=500);
perfect_foresight_solver(stack_solve_algo=0, maxit=50, tolf=1e-8);
