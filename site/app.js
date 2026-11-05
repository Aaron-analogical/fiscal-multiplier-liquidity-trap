import { CALIBRATION, multiplier } from "./simple_model.js";

const COLORS = { normal: "#2a78d6", trap: "#eb6834", grid: "#e6e5e0", text: "#52514e" };
const NO_SOLUTION = "No meaningful solution";
const $ = (id) => document.getElementById(id);
const format = (value) => value.toFixed(2);

function lineChart(canvas, xTitle, yTitle, labels) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Normal times", data: [], borderColor: COLORS.normal, backgroundColor: COLORS.normal,
          borderWidth: 2, pointRadius: 0, pointHitRadius: 12 },
        { label: "Liquidity trap", data: [], borderColor: COLORS.trap, backgroundColor: COLORS.trap,
          borderWidth: 2, pointRadius: 0, pointHitRadius: 12 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { color: COLORS.text, boxWidth: 14, boxHeight: 2 } },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y.toFixed(2)}` } },
      },
      scales: {
        x: { title: { display: true, text: xTitle, color: COLORS.text },
             ticks: { color: COLORS.text, maxTicksLimit: 6 }, grid: { display: false } },
        y: { title: { display: true, text: yTitle, color: COLORS.text },
             ticks: { color: COLORS.text }, grid: { color: COLORS.grid } },
      },
    },
  });
}

function setTile(id, value) {
  const tile = $(id);
  const empty = value === null || value === undefined;
  tile.textContent = empty ? NO_SOLUTION : format(value);
  tile.classList.toggle("empty", empty);
}

const shares = Array.from({ length: 21 }, (_, i) => i / 20);
const simpleChart = lineChart($("simple-chart"), "Share spent on investment (%)", "Multiplier",
  shares.map((share) => Math.round(share * 100)));

function simpleCaption(normal, trap, financing, duration) {
  if (trap === null) {
    return `With a trap of about ${duration} quarters at these settings, deflation and falling demand feed on each other in this linear model, so it gives no usable number. Move trap persistence or price flexibility down.`;
  }
  const other = financing === "lump_sum" ? "labor_tax" : "lump_sum";
  const alpha = Number($("alpha").value);
  const params = currentParams();
  const gap = trap - multiplier(alpha, other, "trap", params);
  const verdict = financing === "labor_tax"
    ? `The labor tax beats the lump-sum tax by ${format(gap)} here: it pushes up inflation, which lowers real interest rates while the policy rate is stuck.`
    : `The lump-sum tax trails the labor tax by ${format(-gap)} here. The full model below reverses this.`;
  return `One extra dollar of spending changes GDP by ${format(normal)} dollars in normal times and ${format(trap)} dollars in a trap. ${verdict}`;
}

function currentParams() {
  return { ...CALIBRATION, p: Number($("p").value), kappa: Number($("kappa").value) };
}

function updateSimple() {
  const financing = document.querySelector("input[name=simple-financing]:checked").value;
  const alpha = Number($("alpha").value);
  const params = currentParams();
  const duration = (1 / (1 - params.p)).toFixed(1);
  $("alpha-out").textContent = `${Math.round(alpha * 100)}%`;
  $("p-out").textContent = `${params.p.toFixed(2)} (about ${duration} quarters)`;
  $("kappa-out").textContent = params.kappa.toFixed(3);

  const normal = multiplier(alpha, financing, "normal", params);
  const trap = multiplier(alpha, financing, "trap", params);
  setTile("simple-normal", normal);
  setTile("simple-trap", trap);
  $("simple-caption").textContent = simpleCaption(normal, trap, financing, duration);

  simpleChart.data.datasets[0].data = shares.map((s) => multiplier(s, financing, "normal", params));
  simpleChart.data.datasets[1].data = shares.map((s) => multiplier(s, financing, "trap", params));
  simpleChart.update();
}

function pick(rows, financing, alpha, build, gamma, state) {
  return rows.find((r) => r.financing === financing && r.alpha === alpha
    && r.build_time === build && r.gamma_n === gamma && r.state === state);
}

function startFullModel(rows) {
  const quarters = Array.from({ length: 51 }, (_, i) => i);
  const chart = lineChart($("full-chart"), "Quarters after the shock", "GDP change (%)", quarters);

  function update() {
    const financing = $("financing").value;
    const [alpha, build] = $("mix").value.split("-").map(Number);
    const sensitivity = financing === "debt" && alpha === 1 && build === 16;
    $("gamma-field").hidden = !sensitivity;
    const gamma = sensitivity ? Number($("gamma").value) : 0.1;

    const normal = pick(rows, financing, alpha, build, gamma, "normal");
    const trap = pick(rows, financing, alpha, build, gamma, "trap");
    setTile("full-normal", normal ? normal.present_value : null);
    setTile("full-trap", trap.present_value);
    if (!normal) {
      $("full-normal").textContent = "Not in the thesis";
    }

    const lumpSum = pick(rows, "lump_sum", alpha, build, 0.1, "trap");
    let caption = `In a trap, the total effect is ${format(trap.present_value)} per dollar and the first-quarter effect is ${format(trap.impact)}.`;
    if (financing !== "lump_sum") {
      const gap = lumpSum.present_value - trap.present_value;
      caption += gap > 0
        ? ` That is ${format(gap)} below the lump-sum tax (${format(lumpSum.present_value)}), because higher taxes last beyond the trap.`
        : ` That is level with or above the lump-sum tax (${format(lumpSum.present_value)}).`;
    }
    $("full-caption").textContent = caption;

    chart.data.datasets[0].data = normal ? normal.path.gdp : [];
    chart.data.datasets[1].data = trap.path.gdp;
    chart.update();

    const cell = (row, key) => (row ? format(row[key]) : "Not in the thesis");
    $("full-table").innerHTML = [["First quarter", "impact"], ["Total effect", "present_value"]]
      .map(([name, key]) => `<tr><td>${name}</td><td>${cell(normal, key)}</td><td>${cell(trap, key)}</td></tr>`)
      .join("");
  }

  ["financing", "mix", "gamma"].forEach((id) => $(id).addEventListener("change", update));
  update();
}

["alpha", "p", "kappa"].forEach((id) => $(id).addEventListener("input", updateSimple));
document.querySelectorAll("input[name=simple-financing]")
  .forEach((input) => input.addEventListener("change", updateSimple));
updateSimple();

fetch("data/full_model.json")
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((data) => startFullModel(data.scenarios))
  .catch(() => {
    $("load-error").hidden = false;
    $("full-results").hidden = true;
  });
