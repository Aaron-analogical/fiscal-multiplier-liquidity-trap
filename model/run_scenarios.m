% Solve every scenario in results/raw/scenario_list.json. Writes one CSV per
% scenario and results/raw/manifest.json. Stops at the first failed solve.
addpath(getenv('DYNARE_MATLAB'));
raw_dir = fullfile('..', 'results', 'raw');
manifest_path = fullfile(raw_dir, 'manifest.json');
spec = jsondecode(fileread(fullfile(raw_dir, 'scenario_list.json')));
list = spec.scenarios;
manifest.config_hash = spec.config_hash;
manifest.model_hash = spec.model_hash;
manifest.dynare_version = dynare_version();
manifest.scenarios = struct();

for n = 1:numel(list)
  s = list(n);
  debt = strcmp(s.financing, 'debt');
  eta = strcmp(s.financing, 'lump_sum');
  command = sprintf(['dynare fiscal -DDEBT=%d -DETA=%d -DALPHA=%g -DBUILD=%d ' ...
    '-DGAMMA_N=%g -DEPS_ZETA=%g -DEPS_G=%g noclearall nolog nograph console'], ...
    debt, eta, s.alpha, s.build_time, s.gamma_n, s.eps_zeta, s.eps_g);
  eval(command);
  global oo_ M_;
  entry = struct('converged', logical(oo_.deterministic_simulation.status), ...
                 'zlb_quarters', 0);
  if ~entry.converged
    manifest.scenarios.(s.id) = entry;
    fid = fopen(manifest_path, 'w');
    fputs(fid, jsonencode(manifest));
    fclose(fid);
    fprintf(stderr, 'Scenario %s did not converge\n', s.id);
    exit(1);
  end
  names = cellstr(M_.endo_names);
  sim = oo_.endo_simul(:, (M_.maximum_lag + 1):end);
  pick = @(v) sim(strcmp(names, v), :)';
  steady_value = @(v) oo_.steady_state(strcmp(names, v));
  y = pick('y'); g = pick('g'); c = pick('c'); pie = pick('pie');
  ii = pick('ii'); tau = pick('tau');
  if debt
    d = pick('d');
  else
    d = zeros(size(y));
  end
  % Real rate between t and t+1. The last simulated row only supplies leads.
  count = numel(y) - 1;
  rr = (1 + ii(1:count)) ./ (1 + pie(2:count + 1)) - 1;
  keep = 1:count;
  rows = [(0:count - 1)' y(keep) g(keep) c(keep) pie(keep) ii(keep) ...
          tau(keep) d(keep) rr repmat(steady_value('y'), count, 1) ...
          repmat(steady_value('g'), count, 1)];
  csv_path = fullfile(raw_dir, [s.id '.csv']);
  fid = fopen(csv_path, 'w');
  fputs(fid, "t,y,g,c,pie,ii,tau,d,rr,y_ss,g_ss\n");
  fclose(fid);
  dlmwrite(csv_path, rows, '-append', 'precision', 12);
  entry.zlb_quarters = sum(ii(keep) < 1e-9);
  manifest.scenarios.(s.id) = entry;
end

fid = fopen(manifest_path, 'w');
fputs(fid, jsonencode(manifest));
fclose(fid);
disp('All scenarios solved');
