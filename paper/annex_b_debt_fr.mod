%------------------------------------------------------------------------------------
% 1. Declaration
%------------------------------------------------------------------------------------

var y g tau d ii pie T y_n c Uc Un Q gi k n mc w zeta;

//exo
varexo eps_zeta epsg;

parameters alpha Beta PSI sigma rb Theta phi delta gamma gamma_n a b KA phipi rho
rho_zeta rho_n pr gbar alphabar deltatild
gi_ss d_ss T_ss Q_ss ii_ss mc_ss pie_ss g_ss n_ss k_ss y_ss y_n_ss Uc_ss Un_ss c_ss
w_ss tau_ss phi_y rho_R;

%------------------------------------------------------------------------------------
% 2. Parameters
%------------------------------------------------------------------------------------
Beta = 0.99;
PSI = 5/0.03;
sigma = 1;
delta = 0.025;
gamma = 0.29;
gamma_n = 0.1;
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

//États stationnaires
tau_ss = 0;
mc_ss = (Theta-1)/Theta;
n_ss = ((1-gamma)/gamma*(1-gbar)/a*(1/mc_ss)*1/(1-tau_ss)+1)^(-1);
c_ss = (((1-gbar)*n_ss^a*(alphabar*gbar)^b*(delta*(1-gbar))^(-b)))^(1/(1-b));
Uc_ss = gamma*c_ss^(gamma*(1-sigma)-1)*(1-n_ss)^((1-gamma)*(1-sigma));
Un_ss = -(1-gamma)*c_ss^(gamma*(1-sigma))*(1-n_ss)^((1-gamma)*(1-sigma)-1);
Q_ss = 1;
k_ss = 1/delta*alphabar*gbar/(1-gbar)*c_ss;
g_ss = delta*k_ss/alphabar;

y_ss = c_ss + g_ss;
y_n_ss = a*y_ss/n_ss;
w_ss = (1-gamma)/(1-n_ss)*c_ss/gamma*1/(1-tau_ss);
//w_ss = mc_ss*a*y_ss/n_ss;
pie_ss = 0;
ii_ss = rb;
gi_ss = alphabar*g_ss;
T_ss = g_ss;
d_ss = tau_ss*w_ss*n_ss/ii_ss; // niveau de la dette ontenu résiduellement. Pour avoir le ratio dette/PIB annuel, il faut calculer d_ss/(4*y_ss)

%------------------------------------------------------------------------------------
% 3. Model
%------------------------------------------------------------------------------------

model;

//**********************************Fonctions auxiliaires****************************

// dérivé de U par rapport à c

Uc = gamma*c^(gamma*(1-sigma)-1)*(1-n)^((1-gamma)*(1-sigma));

// dérivé de U par rapport à n
Un = -(1-gamma)*c^(gamma*(1-sigma))*(1-n)^((1-gamma)*(1-sigma)-1);

// dérivé de F(K,N) par rapport à n
y_n = a*y/n;

// Definition of Stochastic discount factor
Q = Uc/Uc(-1);

// *******************************Équations d’équilibre*****************************

//contrainte de ressource (1)
y = c+g+PSI/2*pie^2*y;

//production (2)
y = n^a*k^b;

//labor supply (3)
w = -Un/Uc*1/(1-tau);

//Équation d’Euler (4)
0 = zeta/Uc + (1+ii)/(1+pie(+1))*Beta*Q(+1)-1;

//CPO du problème des firmes de biens intermédiaires (5)
mc = (Theta-1)/Theta + PSI/Theta*pie*(1+pie)
  -PSI/Theta*Q(+1)*y(+1)/y*pie(+1)*(1+pie(+1));

//coût marginal (6)
mc = w/y_n;

//accumulation du capital (7)
k = (1-delta)*k(-1) + gi(-16);

//dépense public en investissement (8)
gi = gi_ss + alpha*(g-g_ss);

//règle de Taylor (9)
ii = max(0,(1+ii_ss)*((1+ii(-1))/(1+ii_ss))^(rho_R)*((1+pie)^phipi*(y/y_ss)^phi_y)^(1-rho_R)-1);
//ii = max(0, rb + phipi*pie);

//financement par dette et taxe sur le revenu du travail (10)
g + ii*d(-1) = T + tau*w*n + d-d(-1);

//taxe forfaitaire (11)
T = T_ss;

//processus des dépenses publiques (12)
(g-g_ss)/y_ss = rho*(g(-1)-g_ss)/y_ss + epsg;

//processus de la taxe (13)

//tau = tau_ss+gamma_n*(d-d_ss)+epsn;

tau = (1-rho_n)*tau_ss + rho_n*tau(-1) + (1-rho_n)*gamma_n*(d(-1)/y-d_ss/y_ss);

//Choc de préférence pour la liquidité (14)
zeta = rho_zeta*zeta(-1)+eps_zeta;

end;

%------------------------------------------------------------------------------------
% 4. Computation
%------------------------------------------------------------------------------------

//%------Initial values
initval;
d = d_ss;
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
var eps_zeta;
periods 1;
values 0.01;
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
dt_pr = 100*(d./(4*y));

savefile = 'sm_eq.mat';
save(savefile, 'yt_pr', 'gt_pr');
h = 30;

//***************************************Graphiques**********************************

figure(1);
subplot(231);
plot(yt_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('déviation en % de l''état stationnaire')
set(gca,'fontsize',6.5)
title('PIB', 'Fontsize', 8)

subplot(232);
plot(gt_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('% du PIB stationnaire')

set(gca,'fontsize',6.5)
title('Dépenses publiques', 'Fontsize', 8)
subplot(233);
plot(taut_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('%')
set(gca,'fontsize',6.5)
title('Taux de taxe', 'Fontsize', 8)
subplot(234);
plot(dt_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('%')
//axis([0 h -3 3])
set(gca,'fontsize',6.5)
title('Ratio Dette/PIB', 'Fontsize', 8)
subplot(235);
plot(iit_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('% (annuel)')
//axis([0 h -1 5])
set(gca,'fontsize',6.5)
title('Taux d''intérêt nominal', 'Fontsize', 8)
subplot(236);
plot(piet_pr(2:h),'-','LineWidth',1.5,'color','b');
grid on
ylabel('% (annuel)')
set(gca,'fontsize',6.5)
title('Taux d''inflation', 'Fontsize', 8)
fig = gcf;
fig.PaperPositionMode = 'auto';
print(gcf,'-dpdf','Figure_1','-bestfit');
