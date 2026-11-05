%------------------------------------------------------------------------------------
% 1. Declaration
%------------------------------------------------------------------------------------

var y g y_n c Uc Un Q T gi k n pie ii mc w tau zeta;

//exo
varexo eps_zeta epsg;

parameters eta Beta PSI sigma rb Theta phi delta gamma gamma_n a b KA phipi rho
rho_zeta rho_n pr gbar alphabar deltatild
gi_ss T_ss Q_ss ii_ss mc_ss pie_ss g_ss n_ss k_ss y_ss y_n_ss Uc_ss Un_ss c_ss w_ss
tau_ss phi_y rho_R alpha;

%------------------------------------------------------------------------------------
% 2. Parameters
%------------------------------------------------------------------------------------
eta = 0; // 1 for lump-sum financing, 0 for distortionary tax
Beta = 0.99;
PSI = 5/0.03;
sigma = 1;
delta = 0.025;
gamma = 0.29;
gamma_n = 0.025;
a = 1;
b = 0.08;
phipi = 1.5;
rho = 0.8;
rho_zeta = 0.95;
rho_n = 0.5;
KA = 0.03;
gbar = 0.2;
alphabar = 0.23;
Theta = 6;
rb = (1/Beta)-1;
phi = 0.75;
deltatild = delta/(gbar*alphabar);
phi_y = 0.05;
rho_R = 0;
alpha = 1;

//Steady states
tau_ss = 0;
mc_ss = (Theta-1)/Theta;
n_ss = ((1-gamma)/gamma*(1-gbar)/a*(1/mc_ss)+1)^(-1);
c_ss = (((1-gbar)*n_ss^a*(alphabar*gbar)^b*(delta*(1-gbar))^(-b)))^(1/(1-b));
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
piestar_ss = 0;
ii_ss = rb;
gi_ss = alphabar*g_ss;

%------------------------------------------------------------------------------------
% 3. Model
%------------------------------------------------------------------------------------

model;

//*******************************Auxiliary functions******************************

// derivative of U with respect to c

Uc = gamma*c^(gamma*(1-sigma)-1)*(1-n)^((1-gamma)*(1-sigma));

// derivative of U with respect to n
Un = -(1-gamma)*c^(gamma*(1-sigma))*(1-n)^((1-gamma)*(1-sigma)-1);

// derivative of F(K,N) with respect to n
y_n = a*y/n;

// Stochastic discount factor
Q = Uc/Uc(-1);

// ******************************Equilibrium equations*******************************

//resource constraint (1)
y = c+g+PSI/2*pie^2*y;

//production (2)
y = n^a*k^b;

//Labor supply (3)
w = -Un/Uc*1/(1-tau);

//Euler equation (4)
0 = zeta/Uc + (1+ii)/(1+pie(+1))*Beta*Q(+1)-1;

//FOC of the intermediate-goods firms' problem (5)
mc = (Theta-1)/Theta + PSI/Theta*pie*(1+pie)
  -PSI/Theta*Q(+1)*y(+1)/y*pie(+1)*(1+pie(+1));

//marginal cost (6)
mc = w/y_n;

//capital accumulation (7)
k = (1-delta)*k(-1) + gi;

//public investment spending (8)
gi = gi_ss + alpha*(g-g_ss);

//Taylor rule (9)
ii = max(0,(1+ii_ss)*((1+ii(-1))/(1+ii_ss))^(rho_R)*((1+pie)^phipi*(y/y_ss)^phi_y)^(1-rho_R)-1);
//ii = max(0, rb + phipi*pie);

//labor income tax financing (10)
g = T + tau*(w*n);

//lump-sum tax (11)
T = eta*g + (1-eta)*T_ss;

//government spending process (12)
(g-g_ss)/y_ss = rho*(g(-1)-g_ss)/y_ss + epsg;

//liquidity preference shock (13)
zeta = rho_zeta*zeta(-1)+eps_zeta;

end;

%------------------------------------------------------------------------------------
% 4. Computation
%------------------------------------------------------------------------------------

//%------Initial values
initval;
c = c_ss;
T = T_ss;
k = k_ss;
y = y_ss;
n = n_ss;
ii = ii_ss;
w = w_ss;
tau = tau_ss;
pie = pie_ss;
mc = mc_ss;
g = g_ss;
gi = gi_ss;
Uc = Uc_ss;
Un = Un_ss;
y_n = y_n_ss;
Q = Q_ss;
zeta = 0;
end;

steady;

resid(1);

check;

shocks;
//var eps_zeta;
//periods 1;
//values 0.0261;
var epsg;
periods 1;
values 0.01;
end;

//check;
options_.simul.maxit=10;
options_.dynatol.f=1e-8;
simul(periods=500,stack_solve_algo=0);

yt_pr = 100*(y-y_ss)/y_ss;
gt_pr = 100*(g-g_ss)/y_ss;
ct_pr = 100*(c-c_ss)/c_ss;
piet_pr = 400*pie;
iit_pr = 400*ii;
taut_pr = 100*tau;

savefile = 'sm_eq.mat';
save(savefile, 'yt_pr', 'gt_pr');
h = 30;

//***********************************Figures**************************************

figure(1);
subplot(231);
plot(yt_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('deviation in % from steady state')
set(gca,'fontsize',6.5)
title('GDP', 'Fontsize', 8)

subplot(232);
plot(gt_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('% of steady-state GDP')
set(gca,'fontsize',6.5)
title('Government spending', 'Fontsize', 8)

subplot(233);
plot(taut_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('%')
axis([0 h -2 2])

set(gca,'fontsize',6.5)
title('Tax rate', 'Fontsize', 8)
subplot(234);
plot(ct_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('deviation in % from steady state')
//axis([0 h -3 3])
set(gca,'fontsize',6.5)
title('Consumption', 'Fontsize', 8)
subplot(235);
plot(iit_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('% (annual)')
axis([0 h -1 5])
set(gca,'fontsize',6.5)
title('Nominal interest rate', 'Fontsize', 8)
subplot(236);
plot(piet_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('% (annual)')
set(gca,'fontsize',6.5)
title('Inflation rate', 'Fontsize', 8)

fig = gcf;
fig.PaperPositionMode = 'auto';
print(gcf,'-dpdf','Figure_1','-bestfit');
