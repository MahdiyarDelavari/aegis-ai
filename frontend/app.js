const API_BASE = window.AEGIS_API_BASE || "";
const FLOW_PAGE_SIZE = 12;

const state = {
  flowPage: 1,
  flowLabel: "",
  overview: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function formatNumber(value) {
  return new Intl.NumberFormat("en-US").format(value ?? 0);
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatBytes(value) {
  const amount = Number(value || 0);
  if (amount < 1000) return `${formatNumber(amount)} B`;
  if (amount < 1_000_000) return `${(amount / 1000).toFixed(1)} KB`;
  return `${(amount / 1_000_000).toFixed(1)} MB`;
}

async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json();
}

function showError(message) {
  const alert = $("#app-alert");
  alert.textContent = message;
  alert.hidden = false;
}

function clearError() {
  $("#app-alert").hidden = true;
}

function setMetric(name, value) {
  $$(`[data-metric="${name}"]`).forEach((element) => {
    element.textContent = typeof value === "number" ? formatNumber(value) : value;
  });
}

function renderOverview(data) {
  state.overview = data;
  setMetric("total_flows", data.total_flows);
  setMetric("attack_flows", data.attack_flows);
  setMetric("normal_flows", data.normal_flows);
  setMetric("unique_protocols", data.unique_protocols);
  setMetric("attack_percentage", data.attack_percentage);
  $("#donut-total").textContent = formatNumber(data.total_flows);
}

function renderClasses(classes) {
  const attack = classes.find((item) => item.label === 1);
  const normal = classes.find((item) => item.label === 0);
  const attackPercentage = attack?.percentage || 0;
  $("#class-donut").style.background =
    `conic-gradient(var(--orange) 0 ${attackPercentage}%, var(--cyan) ${attackPercentage}% 100%)`;

  $("#class-legend").innerHTML = [
    { item: attack, label: "Attack", tone: "attack" },
    { item: normal, label: "Normal", tone: "normal" },
  ]
    .filter(({ item }) => item)
    .map(
      ({ item, label, tone }) => `
        <div class="legend-item">
          <span class="legend-dot ${tone}"></span>
          <strong>${formatNumber(item.count)}</strong>
          <span>${label} / ${item.percentage}%</span>
        </div>
      `,
    )
    .join("");
}

function renderAttacks(attacks) {
  const max = attacks[0]?.count || 1;
  $("#attack-list").innerHTML =
    attacks.length === 0
      ? '<div class="empty-state">No attack categories found.</div>'
      : attacks
          .slice(0, 6)
          .map(
            (attack) => `
              <div class="bar-row">
                <div class="bar-label">
                  <span>${attack.attack_category}</span>
                  <span>${formatNumber(attack.count)}</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill" style="width: ${(attack.count / max) * 100}%"></div>
                </div>
              </div>
            `,
          )
          .join("");
}

function renderProtocols(protocols) {
  const max = protocols[0]?.count || 1;
  $("#protocol-list").innerHTML =
    protocols.length === 0
      ? '<div class="empty-state">No protocols found.</div>'
      : protocols
          .slice(0, 6)
          .map(
            (protocol) => `
              <div class="protocol-row">
                <span class="protocol-name">${protocol.protocol || "unknown"}</span>
                <div class="protocol-bar">
                  <span style="width: ${(protocol.count / max) * 100}%"></span>
                </div>
                <span class="protocol-count">${formatNumber(protocol.count)}</span>
              </div>
            `,
          )
          .join("");
}

function renderFlows(data) {
  $("#flow-count").textContent = `${formatNumber(data.total)} matching flows`;
  $("#page-number").textContent = `Page ${data.page}`;
  $("#previous-page").disabled = data.page <= 1;
  $("#next-page").disabled = data.page * data.size >= data.total;
  $("#flows-body").innerHTML =
    data.items.length === 0
      ? '<tr><td class="table-message" colspan="7">No flows match this filter.</td></tr>'
      : data.items
          .map(
            (flow) => `
              <tr>
                <td>${formatNumber(flow.source_id)}</td>
                <td><span class="classification ${flow.label === 1 ? "attack" : "normal"}">${flow.label === 1 ? "Attack" : "Normal"}</span></td>
                <td>${flow.attack_cat || "—"}</td>
                <td>${flow.proto || "—"}</td>
                <td>${Number(flow.dur || 0).toFixed(3)}s</td>
                <td>${formatBytes(flow.sbytes)}</td>
                <td>${formatBytes(flow.dbytes)}</td>
              </tr>
            `,
          )
          .join("");
}

function renderPipeline(runs) {
  $("#pipeline-body").innerHTML =
    runs.length === 0
      ? '<tr><td class="table-message" colspan="6">No pipeline runs found.</td></tr>'
      : runs
          .map(
            (run) => `
              <tr>
                <td>#${formatNumber(run.run_id)}</td>
                <td><span class="run-status ${run.status}">${run.status}</span></td>
                <td>${formatNumber(run.processed_flows)}</td>
                <td>${formatNumber(run.rejected_rows)}</td>
                <td>${formatDate(run.started_at)}</td>
                <td>${formatDate(run.finished_at)}</td>
              </tr>
            `,
          )
          .join("");
}

async function loadOverview() {
  const [overview, classes, attacks, protocols] = await Promise.all([
    getJson("/api/overview"),
    getJson("/api/traffic/classes"),
    getJson("/api/attacks/top?limit=6"),
    getJson("/api/protocols/top?limit=6"),
  ]);
  renderOverview(overview);
  renderClasses(classes);
  renderAttacks(attacks);
  renderProtocols(protocols);
}

async function loadFlows() {
  const query = new URLSearchParams({
    page: state.flowPage,
    size: FLOW_PAGE_SIZE,
  });
  if (state.flowLabel !== "") query.set("label", state.flowLabel);
  renderFlows(await getJson(`/api/flows?${query}`));
}

async function loadPipeline() {
  renderPipeline(await getJson("/api/pipeline/runs?limit=20"));
}

async function checkHealth() {
  const dot = $("#system-status-dot");
  const label = $("#system-status-label");
  try {
    await getJson("/api/health");
    dot.classList.remove("is-offline");
    label.textContent = "API connected";
  } catch {
    dot.classList.add("is-offline");
    label.textContent = "API unavailable";
  }
}

async function refreshAll() {
  clearError();
  $("#refresh-button").disabled = true;
  try {
    await Promise.all([loadOverview(), loadFlows(), loadPipeline(), checkHealth()]);
    $("#last-updated").textContent = `Updated ${new Intl.DateTimeFormat("en-US", {
      timeStyle: "short",
    }).format(new Date())}`;
  } catch (error) {
    showError(`Unable to load dashboard data. ${error.message}`);
  } finally {
    $("#refresh-button").disabled = false;
  }
}

function showPage(section) {
  const title = section === "flows" ? "Network flows" : section === "pipeline" ? "Pipeline runs" : "Overview";
  $("#page-title").textContent = title;
  $$(".page-section").forEach((page) => {
    const active = page.dataset.page === section;
    page.hidden = !active;
    page.classList.toggle("is-visible", active);
  });
  $$(".nav-link").forEach((link) => {
    link.classList.toggle("is-active", link.dataset.section === section);
  });
  if (section === "flows") loadFlows().catch((error) => showError(error.message));
  if (section === "pipeline") loadPipeline().catch((error) => showError(error.message));
}

function bindNavigation() {
  $$("[data-section], [data-section-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const section = link.dataset.section || link.dataset.sectionLink;
      window.history.replaceState({}, "", `#${section}`);
      showPage(section);
    });
  });
  window.addEventListener("hashchange", () => {
    showPage(window.location.hash.slice(1) || "overview");
  });
}

$("#refresh-button").addEventListener("click", refreshAll);
$("#flow-label-filter").addEventListener("change", (event) => {
  state.flowLabel = event.target.value;
  state.flowPage = 1;
  loadFlows().catch((error) => showError(error.message));
});
$("#previous-page").addEventListener("click", () => {
  if (state.flowPage > 1) {
    state.flowPage -= 1;
    loadFlows().catch((error) => showError(error.message));
  }
});
$("#next-page").addEventListener("click", () => {
  state.flowPage += 1;
  loadFlows().catch((error) => showError(error.message));
});

bindNavigation();
showPage(window.location.hash.slice(1) || "overview");
refreshAll();
