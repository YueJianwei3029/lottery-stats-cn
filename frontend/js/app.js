// ==========================================
// 彩票数据统计与可视化系统 v2.0 — 主逻辑
// 适配全新深色仪表盘界面
// ==========================================

const API_BASE = window.APP_CONFIG ? window.APP_CONFIG.API_BASE : "/api";

const HAS_EXTEND = {
  lottery_dlt: true,
  lottery_7xc: true,
  lottery_ssq: true,
  lottery_pl5: true,
  lottery_pl3: true,
};

let currentType    = "lottery_dlt";
let currentPage    = 1;
let totalPages     = 1;
let currentPageSize = 20;
let chartInstances = {};
let currentView    = "query";
let currentExtendSub = "dist";

// ECharts 主题配置（深色）
const ECHARTS_THEME = {
  backgroundColor: "transparent",
  textStyle: { color: "#8b949e", fontFamily: "-apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif" },
  title: { textStyle: { color: "#e6edf3", fontSize: 13, fontWeight: 600 } },
  legend: { textStyle: { color: "#8b949e", fontSize: 11 } },
  tooltip: {
    backgroundColor: "#1c2433",
    borderColor: "#30363d",
    borderWidth: 1,
    textStyle: { color: "#e6edf3", fontSize: 12 },
    extraCssText: "border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.6);",
  },
  xAxis: { axisLine: { lineStyle: { color: "#30363d" } }, axisTick: { lineStyle: { color: "#30363d" } }, axisLabel: { color: "#8b949e", fontSize: 11 }, splitLine: { lineStyle: { color: "#21303f" } } },
  yAxis: { axisLine: { lineStyle: { color: "#30363d" } }, axisTick: { lineStyle: { color: "#30363d" } }, axisLabel: { color: "#8b949e", fontSize: 11 }, splitLine: { lineStyle: { color: "#21303f" } } },
};

// 颜色板
const COLORS = ["#58a6ff", "#3fb950", "#f0883e", "#bc8cff", "#39d9c8", "#f85149", "#e3b341", "#ff7b7b"];

// ── 热力图 Y 轴短标签 ─────────────────────────────────────
// 将 "pos_front_1" → "前1", "pos_back_2" → "后2",
//      "pos_red_1"  → "红1", "pos_blue_1" → "蓝",
//      "pos_num_1"   → "位1"
function buildHeatmapYLabels(positions) {
  return positions.map(function(p) {
    if (p.indexOf("front_") !== -1) return "前" + p.match(/(\d+)$/)[1];
    if (p.indexOf("back_")  !== -1) return "后" + p.match(/(\d+)$/)[1];
    if (p.indexOf("red_")   !== -1) return "红" + p.match(/(\d+)$/)[1];
    if (p.indexOf("blue_")  !== -1) return "蓝";
    if (p.indexOf("num_")   !== -1) return "位" + p.match(/(\d+)$/)[1];
    return p.replace("pos_", "");
  });
}

// ── 帮助说明文字 ──────────────────────────────────────────────
const CHART_HELP = {
  extHeat: {
    title: "位置×号码 热力图",
    text: "统计每个位置（纵轴）各个号码（横轴）在选定日期范围内的出现次数。<br><br><b>原理：</b>按日期范围筛选数据（默认全量），遍历所有期数，累计每个位置上各号码出现的频次。<br><br><b>读法：</b>颜色越深表示该位置该号码出现次数越多，可快速识别各位置的号码分布规律。<br><br><b>注：</b>各彩种号码范围不同（排列类0-9，双色球红球1-33，大乐透前区1-35），X轴范围会相应变化。",
  },
  extHotCold: {
    title: "冷热号",
    text: "统计选定日期范围内各号码的出现频次。<br><br><b>热号：</b>出现次数最多的号码（Top5~10），即高频号码。<br><b>冷号：</b>出现次数最少或从未出现的号码，即长期未出的号码。<br><br><b>原理：</b>按日期范围筛选数据，统计每个号码出现次数并按降序排列。若未指定日期，默认取最近50期；若指定了日期范围，则使用范围内全量数据。<br><br><b>读法：</b>左侧（红色）为热号，右侧（蓝色）为冷号。",
  },
  extPeriod: {
    title: "和值跨度走势",
    text: "逐期展示每期的号码之和与号码极差（最大值-最小值）。<br><br><b>和值：</b>当期所有号码相加的总和，反映号码整体的集中趋势。<br><b>跨度：</b>当期最大号码与最小号码的差值，反映号码的分散程度。<br><br><b>原理：</b>逐期计算和值与跨度，以折线图呈现变化趋势。若未指定日期，默认取最近500期；指定日期范围则使用范围内全量数据。可通过底部控件调整显示期数（20~200期）。",
  },
  extRatio: {
    title: "奇偶比/大小比趋势",
    text: "逐期展示每期奇数号码个数与偶数号码个数的比例，以及大号个数与小号个数的比例。<br><br><b>奇偶比：</b>奇数数量 : 偶数数量（如3:2表示3奇2偶）。<br><b>大小比：</b>大号数量 : 小号数量，分界值各彩种不同（排列类≥5为大，双色球红球≥17为大，大乐透前区≥18为大）。<br><br><b>原理：</b>逐期统计奇数/偶数个数和大号/小号个数，折线图展示趋势变化。若未指定日期，默认取最近500期。可通过底部控件调整显示期数（20~200期）。",
  },
};

function showChartHelp(key) {
  const h = CHART_HELP[key];
  if (!h) return;
  const overlay = document.createElement("div");
  overlay.className = "chart-help-overlay";
  overlay.innerHTML = `
    <div class="chart-help-dialog">
      <h3>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        ${h.title}
      </h3>
      <p>${h.text}</p>
      <button class="help-close" onclick="this.closest('.chart-help-overlay').remove()">知道了</button>
    </div>`;
  overlay.addEventListener("click", (e) => { if (e.target === overlay) overlay.remove(); });
  document.body.appendChild(overlay);
}

function addHelpBtn(box, key) {
  const btn = document.createElement("span");
  btn.className = "chart-tip";
  btn.title = "点击查看说明";
  btn.textContent = "?";
  btn.onclick = (e) => { e.stopPropagation(); showChartHelp(key); };
  box.appendChild(btn);
}

// ── 辅助函数 ──────────────────────────────────────────────────
function div(cls, id, extraCls) {
  const d = document.createElement("div");
  d.className = cls + (extraCls ? " " + extraCls : "");
  if (id) d.id = id;
  return d;
}

// ── 初始化 ────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initMobileMenu();
  initNav();
  initViewToggle();
  initMobileNav();
  initControls();
  initPageSize();
  initAdvancedSubMenu();
  switchType(currentType);
});

// ── 移动端侧边栏 ──────────────────────────────────────────────
function initMobileMenu() {
  const toggle  = document.getElementById("menuToggle");
  const sidebar = document.getElementById("lotteryNav");
  const overlay = document.getElementById("sidebarOverlay");

  function openSidebar() {
    sidebar.classList.add("open");
    overlay.classList.add("show");
    toggle.classList.add("open");
  }
  function closeSidebar() {
    sidebar.classList.remove("open");
    overlay.classList.remove("show");
    toggle.classList.remove("open");
  }

  toggle.addEventListener("click", () => {
    sidebar.classList.contains("open") ? closeSidebar() : openSidebar();
  });
  overlay.addEventListener("click", closeSidebar);
  window._closeSidebar = closeSidebar;
}

// ── 彩种导航 ──────────────────────────────────────────────────
function initNav() {
  document.querySelectorAll("#lotteryNav .nav-item").forEach(item => {
    item.addEventListener("click", () => {
      const type = item.dataset.type;
      if (type !== currentType) switchType(type);
      // 移动端点击后关闭侧边栏
      if (window._closeSidebar) window._closeSidebar();
    });
  });
}

function switchType(type) {
  currentType = type;
  currentPage = 1;
  document.querySelectorAll("#lotteryNav .nav-item").forEach(n =>
    n.classList.toggle("active", n.dataset.type === type)
  );
  disposeAllCharts();
  loadQuery();
  if (currentView === "stats")   loadStats();
  if (currentView === "extend")  loadExtendView();
  if (currentView === "advanced") loadAdvancedView();
}

// ── 视图切换（桌面 tab） ─────────────────────────────────────
function initViewToggle() {
  document.querySelectorAll(".view-btn").forEach(btn => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });
}

// ── 移动端底部导航 ────────────────────────────────────────────
function initMobileNav() {
  document.querySelectorAll(".mobile-nav-btn").forEach(btn => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });
}

function switchView(view) {
  if (view === currentView) return;
  currentView = view;

  // 同步两组按钮状态
  document.querySelectorAll(".view-btn").forEach(b =>
    b.classList.toggle("active", b.dataset.view === view)
  );
  document.querySelectorAll(".mobile-nav-btn").forEach(b =>
    b.classList.toggle("active", b.dataset.view === view)
  );

  // 面板切换
  ["viewQuery", "viewStats", "viewExtend", "viewAdvanced"].forEach(id => {
    const el = document.getElementById(id);
    el.classList.toggle("hidden", id !== "view" + capitalize(view));
  });

  if (view === "stats")    loadStats();
  if (view === "extend")   loadExtendView();
  if (view === "advanced") loadAdvancedView();
}

function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

// ── 日期参数 ──────────────────────────────────────────────────
function getDateParam() {
  const ds = document.getElementById("dateStart").value || "";
  const de = document.getElementById("dateEnd").value || "";
  const start = ds ? ds.replace(/-/g, "") : null;
  const end   = de ? de.replace(/-/g, "") : null;
  const params = [];
  if (start) params.push(`date=${start}`);
  if (end)   params.push(`end_date=${end}`);
  return params.length ? "?" + params.join("&") : "";
}

// ── 控件事件 ──────────────────────────────────────────────────
function initControls() {
  document.getElementById("queryBtn").addEventListener("click", () => {
    currentPage = 1;
    loadQuery();
    reloadCurrentView();
  });
  document.getElementById("prevBtn").addEventListener("click", () => {
    if (currentPage > 1) { currentPage--; loadQuery(); }
  });
  document.getElementById("nextBtn").addEventListener("click", () => {
    if (currentPage < totalPages) { currentPage++; loadQuery(); }
  });
}

function initPageSize() {
  document.getElementById("pageSizeSelect").addEventListener("change", () => {
    currentPageSize = parseInt(document.getElementById("pageSizeSelect").value) || 20;
    currentPage = 1;
    loadQuery();
  });
}

function reloadCurrentView() {
  if (currentView === "stats")    loadStats();
  if (currentView === "extend")   loadExtendView();
  if (currentView === "advanced") loadAdvancedView();
}

// ── 数据查询 ──────────────────────────────────────────────────
async function loadQuery() {
  const tableLoading = document.getElementById("tableLoading");
  const tableEmpty   = document.getElementById("tableEmpty");
  const tableContainer = document.getElementById("tableContainer");
  const pagination   = document.getElementById("pagination");

  tableLoading.style.display = "flex";
  tableEmpty.style.display   = "none";
  tableContainer.style.display = "none";
  pagination.style.display   = "none";

  const dateParams = getDateParam();
  const prefix  = dateParams ? (dateParams + "&") : "?";
  const fullUrl = `${API_BASE}/${currentType}/query${prefix}page=${currentPage}&page_size=${currentPageSize}`;

  try {
    const resp = await fetch(fullUrl);
    const json = await resp.json();
    const data = json.data;

    if (!data || !data.records || data.records.length === 0) {
      tableLoading.style.display = "none";
      tableEmpty.style.display   = "flex";
      return;
    }

    renderTable(data.records);
    totalPages = Math.ceil(data.total / data.page_size) || 1;

    document.getElementById("pageInfo").textContent  = data.page;
    document.getElementById("totalPages").textContent = totalPages;
    document.getElementById("totalInfo").textContent = `共 ${data.total} 条`;
    document.getElementById("prevBtn").disabled = currentPage <= 1;
    document.getElementById("nextBtn").disabled = currentPage >= totalPages;

    tableContainer.style.display = "";
    pagination.style.display     = "flex";
  } catch (e) {
    console.error("查询失败:", e);
    tableEmpty.style.display = "flex";
  }
  tableLoading.style.display = "none";
}

// ── 号码列名映射 ──────────────────────────────────────────────
const FIELD_LABELS = {
  id: "序号", draw_num: "期号", draw_date: "开奖日期",
  num_1:"号码1", num_2:"号码2", num_3:"号码3", num_4:"号码4", num_5:"号码5",
  num_6:"号码6", num_7:"号码7",
  red_1:"红1", red_2:"红2", red_3:"红3", red_4:"红4", red_5:"红5", red_6:"红6",
  blue_1:"蓝球",
  front_1:"前1", front_2:"前2", front_3:"前3", front_4:"前4", front_5:"前5",
  back_1:"后1", back_2:"后2",
  special_num:"特别号",
  sales_amount:"销售额", prize_pool:"奖池",
};

// 判断字段对应的球样式
function getBallClass(key) {
  if (key.startsWith("red_"))    return "ball-red";
  if (key === "blue_1")          return "ball-blue";
  if (key.startsWith("front_"))  return "ball-front";
  if (key.startsWith("back_"))   return "ball-back";
  if (key.startsWith("num_"))    return "ball-num";
  if (key === "special_num")     return "ball-special";
  return null;
}

// 给非号码列分配窄列样式
function getNarrowClass(key) {
  if (key === "id")        return "col-narrow col-id";
  if (key === "draw_num")  return "col-narrow col-draw-num";
  if (key === "draw_date") return "col-narrow col-date";
  return "";
}

function renderTable(records) {
  if (!records.length) return;
  const keys = Object.keys(records[0]);

  // 表头
  const thead = document.getElementById("tableHead");
  thead.innerHTML = "<tr>" +
    keys.map(k => {
      var nc = getNarrowClass(k);
      return `<th class="${nc}">${FIELD_LABELS[k] || k}</th>`;
    }).join("") +
    "</tr>";

  // 表体
  const tbody = document.getElementById("tableBody");
  tbody.innerHTML = records.map(r =>
    "<tr>" + keys.map(k => {
      const val = r[k] !== null ? r[k] : "-";
      const cls = getBallClass(k);
      var nc = getNarrowClass(k);
      if (cls && val !== "-") {
        return `<td class="${nc}"><span class="num-ball ${cls}">${String(val).padStart(2, "0")}</span></td>`;
      }
      return `<td class="${nc}">${val}</td>`;
    }).join("") + "</tr>"
  ).join("");
}

// ── 基础统计 ──────────────────────────────────────────────────
async function loadStats() {
  disposeAllCharts();
  const container = document.getElementById("statsContainer");
  container.innerHTML = "";

  const dateParams = getDateParam();
  try {
    const resp = await fetch(`${API_BASE}/${currentType}/stats${dateParams}`);
    const json = await resp.json();
    const data = json.data;
    if (!data || !data.fields) return;

    const fields = data.fields;
    const labels = buildPosLabels(fields);

    if (currentType === "lottery_dlt")     buildDLTStats(container, data, fields, labels);
    else if (currentType === "lottery_ssq") buildSSQStats(container, data, fields, labels);
    else                                    buildNormalStats(container, data, fields, labels);
  } catch (e) {
    console.error("统计加载失败:", e);
  }
}

function buildNormalStats(container, data, fields, labels) {
  const fullRange = buildFullRange(data.freq, fields);
  container.innerHTML = `
    <div class="stats-layout">
      <div class="stats-top"><div class="chart-scroll"><div class="chart-box" id="chartFreq"><span class="chart-tip" title="各位置号码出现次数分布">?</span></div></div></div>
      <div class="stats-bottom">
        <div class="chart-scroll"><div class="chart-box" id="chartOE"></div></div>
        <div class="chart-scroll"><div class="chart-box" id="chartBS"></div></div>
      </div>
    </div>`;
  renderGroupedBar("chartFreq", {
    title: "各位置号码频率",
    xData: fullRange.map(String),
    series: fields.map((f, i) => ({ name: labels[i], data: fullRange.map(n => (data.freq[f] || {})[String(n)] || 0) })),
    xName: "号码", yName: "次数",
  });
  renderStackedBar("chartOE", {
    title: "各位置奇偶分布", yData: labels,
    series: [
      { name: "奇数", data: fields.map(f => (data.odd_even[f] || {}).odd  || 0), color: "#f85149" },
      { name: "偶数", data: fields.map(f => (data.odd_even[f] || {}).even || 0), color: "#58a6ff" },
    ],
  });
  renderStackedBar("chartBS", {
    title: "各位置大小分布", yData: labels,
    series: [
      { name: "大号", data: fields.map(f => (data.big_small[f] || {}).big   || 0), color: "#f0883e" },
      { name: "小号", data: fields.map(f => (data.big_small[f] || {}).small || 0), color: "#3fb950" },
    ],
  });
}

function buildDLTStats(container, data, fields, labels) {
  const fFields = fields.filter(f => f.startsWith("front_"));
  const bFields = fields.filter(f => f.startsWith("back_"));
  const fLabels = buildPosLabels(fFields), bLabels = buildPosLabels(bFields);
  const fRange  = buildFullRange(data.freq, fFields), bRange = buildFullRange(data.freq, bFields);
  container.innerHTML = `
    <div class="stats-dlt">
      <div class="chart-scroll"><div class="chart-full chart-box" id="chartFF"></div></div>
      <div class="chart-scroll"><div class="chart-full chart-box" id="chartBF"></div></div>
      <div class="chart-half-row">
        <div class="chart-scroll"><div class="chart-box" id="chartOE"></div></div>
        <div class="chart-scroll"><div class="chart-box" id="chartBS"></div></div>
      </div>
    </div>`;
  renderGroupedBar("chartFF", {
    title: "前区号码频率 (1-35)",
    xData: fRange.map(String),
    series: fFields.map((f, i) => ({ name: fLabels[i], data: fRange.map(n => (data.freq[f] || {})[String(n)] || 0) })),
    xName: "号码", yName: "次数",
  });
  renderGroupedBar("chartBF", {
    title: "后区号码频率 (1-12)",
    xData: bRange.map(String),
    series: bFields.map((f, i) => ({ name: bLabels[i], data: bRange.map(n => (data.freq[f] || {})[String(n)] || 0) })),
    xName: "号码", yName: "次数",
  });
  renderStackedBar("chartOE", {
    title: "前后区奇偶分布", yData: labels,
    series: [
      { name: "奇数", data: fields.map(f => (data.odd_even[f] || {}).odd  || 0), color: "#f85149" },
      { name: "偶数", data: fields.map(f => (data.odd_even[f] || {}).even || 0), color: "#58a6ff" },
    ],
  });
  renderStackedBar("chartBS", {
    title: "前后区大小分布", yData: labels,
    series: [
      { name: "大号", data: fields.map(f => (data.big_small[f] || {}).big   || 0), color: "#f0883e" },
      { name: "小号", data: fields.map(f => (data.big_small[f] || {}).small || 0), color: "#3fb950" },
    ],
  });
}

function buildSSQStats(container, data, fields, labels) {
  const redFields  = fields.filter(f => f.startsWith("red_"));
  const blueFields = fields.filter(f => f.startsWith("blue_"));
  const redLabels  = buildPosLabels(redFields);
  const redRange   = buildFullRange(data.freq, redFields);
  const blueRange  = buildFullRange(data.freq, blueFields);
  container.innerHTML = `
    <div class="stats-dlt">
      <div class="chart-scroll"><div class="chart-full chart-box" id="chartRF"></div></div>
      <div class="chart-scroll"><div class="chart-full chart-box" id="chartBF"></div></div>
      <div class="chart-half-row">
        <div class="chart-scroll"><div class="chart-box" id="chartOE"></div></div>
        <div class="chart-scroll"><div class="chart-box" id="chartBS"></div></div>
      </div>
    </div>`;
  renderGroupedBar("chartRF", {
    title: "红球号码频率 (1-33)",
    xData: redRange.map(String),
    series: redFields.map((f, i) => ({ name: redLabels[i], data: redRange.map(n => (data.freq[f] || {})[String(n)] || 0) })),
    xName: "号码", yName: "次数",
  });
  renderChart("chartBF", {
    title: "蓝球频率 (1-16)",
    xData: blueRange.map(String),
    yData: blueRange.map(n => (data.freq[blueFields[0]] || {})[String(n)] || 0),
    xName: "号码", yName: "次数", seriesName: "蓝球", color: "#58a6ff",
  });
  renderStackedBar("chartOE", {
    title: "红球奇偶分布", yData: redLabels,
    series: [
      { name: "奇数", data: redFields.map(f => (data.odd_even[f] || {}).odd  || 0), color: "#f85149" },
      { name: "偶数", data: redFields.map(f => (data.odd_even[f] || {}).even || 0), color: "#58a6ff" },
    ],
  });
  renderStackedBar("chartBS", {
    title: "红球大小分布", yData: redLabels,
    series: [
      { name: "大号", data: redFields.map(f => (data.big_small[f] || {}).big   || 0), color: "#f0883e" },
      { name: "小号", data: redFields.map(f => (data.big_small[f] || {}).small || 0), color: "#3fb950" },
    ],
  });
}

function buildPosLabels(fields) {
  const map = {
    num_1:"位置1", num_2:"位置2", num_3:"位置3", num_4:"位置4", num_5:"位置5",
    num_6:"位置6", num_7:"位置7",
    red_1:"红球1", red_2:"红球2", red_3:"红球3", red_4:"红球4", red_5:"红球5", red_6:"红球6",
    blue_1:"蓝球",
    front_1:"前区1", front_2:"前区2", front_3:"前区3", front_4:"前区4", front_5:"前区5",
    back_1:"后区1", back_2:"后区2",
  };
  return fields.map(f => map[f] || f);
}

function buildFullRange(freq, fields) {
  const nums = new Set();
  fields.forEach(f => Object.keys(freq[f] || {}).forEach(n => nums.add(parseInt(n))));
  if (nums.size === 0) return [];
  const arr = [...nums].sort((a, b) => a - b);
  const full = [];
  for (let n = arr[0]; n <= arr[arr.length - 1]; n++) full.push(n);
  return full;
}

// ── 扩展统计 ──────────────────────────────────────────────────
function initExtendSubMenu() {
  document.querySelectorAll("#extendSubMenu .sub-btn").forEach(btn => {
    btn.onclick = null;
    btn.addEventListener("click", () => {
      const sub = btn.dataset.sub;
      if (sub === currentExtendSub) return;
      currentExtendSub = sub;
      document.querySelectorAll("#extendSubMenu .sub-btn").forEach(b =>
        b.classList.toggle("active", b.dataset.sub === sub)
      );
      loadExtendCharts();
    });
  });
}

function loadExtendView() {
  const container = document.getElementById("extendContent");
  disposeExtendCharts();
  initExtendSubMenu();

  if (!HAS_EXTEND[currentType]) {
    container.innerHTML = `
      <div class="dev-placeholder">
        <div class="dev-icon">🚧</div>
        <h3>暂无扩展统计</h3>
        <p>该彩种的扩展统计功能正在开发中，敬请期待。</p>
      </div>`;
    return;
  }

  container.innerHTML = '<div id="extendCharts"></div>';
  loadExtendCharts();
}

function disposeExtendCharts() {
  Object.keys(chartInstances).forEach(id => {
    if (id.startsWith("ext") && chartInstances[id]) {
      chartInstances[id].dispose();
      delete chartInstances[id];
    }
  });
}

async function loadExtendCharts() {
  if (currentExtendSub === "dist") await loadDistCharts();
  else                              await loadTrendCharts();
}

// ── 分布分析（热力图 + 冷热号） ───────────────────────────────
async function loadDistCharts() {
  const extCharts = document.getElementById("extendCharts");
  if (!extCharts) return;
  extCharts.innerHTML = "";
  extCharts.className = "extend-layout";

  const dateParams = getDateParam();
  const isBig = currentType === "lottery_dlt" || currentType === "lottery_ssq";

  const heatRow = div("extend-row");
  const heatScroll = div("chart-scroll");
  const heatBox = div("chart-box", "extHeat", isBig ? "chart-full" : "");
  heatScroll.appendChild(heatBox);
  heatRow.appendChild(heatScroll);
  extCharts.appendChild(heatRow);

  const hcRow = div("extend-row");
  const hcScroll = div("chart-scroll");
  const hcBox = div("chart-box", "extHotCold");
  hcScroll.appendChild(hcBox);
  hcRow.appendChild(hcScroll);
  extCharts.appendChild(hcRow);

  // 热力图
  try {
    const r = await fetch(`${API_BASE}/${currentType}/stats/position${dateParams}`).then(r => r.json());
    if (r.data) {
      const positions = Object.keys(r.data);
      const numSet = new Set();
      positions.forEach(p => Object.keys(r.data[p]).forEach(n => numSet.add(parseInt(n))));
      const numRange = Array.from(numSet).sort((a, b) => a - b);
      const heatData = [];
      positions.forEach((p, pi) => {
        numRange.forEach((n, ni) => { heatData.push([ni, pi, r.data[p][String(n)] || 0]); });
      });
      const labels = buildHeatmapYLabels(positions);
      const chart = echarts.init(heatBox);
      chartInstances["extHeat"] = chart;
      addHelpBtn(heatBox, "extHeat");
      chart.setOption({
        ...ECHARTS_THEME,
        title: { text: "位置×号码 热力图", left: "center", top: 6, textStyle: { color: "#e6edf3", fontSize: 13 } },
        tooltip: { ...ECHARTS_THEME.tooltip },
        grid: { left: 60, right: 36, top: 48, bottom: 110 },
        xAxis: { ...ECHARTS_THEME.xAxis, type: "category", data: numRange.map(String), name: "号码", axisLabel: { ...ECHARTS_THEME.xAxis.axisLabel, rotate: numRange.length > 20 ? 45 : 0 } },
        yAxis: { ...ECHARTS_THEME.yAxis, type: "category", data: labels },
        visualMap: { min: 0, calculable: true, orient: "horizontal", left: "center", bottom: 6, textStyle: { color: "#8b949e" }, itemWidth: 14, itemHeight: 140, inRange: { color: ["#1c2433", "#0d4977", "#58a6ff"] } },
        series: [{
          type: "heatmap",
          data: heatData,
          label: { show: false },
          emphasis: { itemStyle: { shadowBlur: 6, shadowColor: "rgba(88,166,255,0.45)" }, label: { show: true, fontSize: 11, color: "#e6edf3", fontWeight: 600 } }
        }],
      });
    }
  } catch (e) { console.error(e); }

  // 冷热号
  try {
    const r = await fetch(`${API_BASE}/${currentType}/stats/hot_cold${dateParams}`).then(r => r.json());
    if (r.data) {
      const hot  = (r.data.hot  || []).reverse();
      const cold = (r.data.cold || []).reverse();
      const chart = echarts.init(hcBox);
      chartInstances["extHotCold"] = chart;
      addHelpBtn(hcBox, "extHotCold");
      chart.setOption({
        ...ECHARTS_THEME,
        title: { text: "冷热号分析", left: "center", top: 6, textStyle: { color: "#e6edf3", fontSize: 13 } },
        tooltip: { ...ECHARTS_THEME.tooltip },
        legend: { data: ["热号", "冷号"], top: 32, textStyle: { color: "#8b949e", fontSize: 11 } },
        grid: [{ left: "5%", top: 72, width: "40%", bottom: 32 }, { left: "55%", top: 72, width: "40%", bottom: 32 }],
        xAxis: [
          { gridIndex: 0, type: "value", ...ECHARTS_THEME.xAxis },
          { gridIndex: 1, type: "value", inverse: true, ...ECHARTS_THEME.xAxis },
        ],
        yAxis: [
          { gridIndex: 0, type: "category", data: hot.map(h => h.number), ...ECHARTS_THEME.yAxis },
          { gridIndex: 1, type: "category", data: cold.map(c => c.number), ...ECHARTS_THEME.yAxis },
        ],
        series: [
          { name: "热号", type: "bar", data: hot.map(h => h.count), xAxisIndex: 0, yAxisIndex: 0, itemStyle: { color: "#f85149", borderRadius: [0, 4, 4, 0] } },
          { name: "冷号", type: "bar", data: cold.map(c => c.count), xAxisIndex: 1, yAxisIndex: 1, itemStyle: { color: "#58a6ff", borderRadius: [0, 4, 4, 0] } },
        ],
      });
    }
  } catch (e) { console.error(e); }
}

// ── 走势分析（和值跨度 + 奇偶比） ────────────────────────────
async function loadTrendCharts() {
  const extCharts = document.getElementById("extendCharts");
  if (!extCharts) return;
  extCharts.innerHTML = "";
  extCharts.className = "extend-layout";

  const dateParams = getDateParam();

  const pRow = div("extend-row"); const pScroll = div("chart-scroll"); const pBox = div("chart-box", "extPeriod"); pScroll.appendChild(pBox); pRow.appendChild(pScroll); extCharts.appendChild(pRow);
  const rRow = div("extend-row"); const rScroll = div("chart-scroll"); const rBox = div("chart-box", "extRatio");  rScroll.appendChild(rBox); rRow.appendChild(rScroll); extCharts.appendChild(rRow);

  function makeDataZoom(recs) {
    const total = recs.length;
    const sv = Math.max(0, total - 100);
    return [
      { type: "slider", startValue: sv, endValue: total - 1, minValueSpan: 20, maxValueSpan: 200, height: 22, bottom: 10, textStyle: { color: "#8b949e" }, borderColor: "#30363d", fillerColor: "rgba(88,166,255,0.15)", handleStyle: { color: "#58a6ff" } },
      { type: "inside", minValueSpan: 20, maxValueSpan: 200 },
    ];
  }

  const trendGrid = { left: 52, right: 20, top: 58, bottom: 98 };

  try {
    const r = await fetch(`${API_BASE}/${currentType}/stats/period_list${dateParams}`).then(r => r.json());
    if (r.data && r.data.records) {
      const recs = r.data.records.reverse();
      const chart = echarts.init(pBox);
      chartInstances["extPeriod"] = chart;
      addHelpBtn(pBox, "extPeriod");
      chart.setOption({
        ...ECHARTS_THEME,
        title: { text: "和值 / 跨度走势", left: "center", top: 6, textStyle: { color: "#e6edf3", fontSize: 13 } },
        tooltip: { trigger: "axis", ...ECHARTS_THEME.tooltip },
        legend: { data: ["和值", "跨度"], top: 30, textStyle: { color: "#8b949e", fontSize: 11 } },
        grid: trendGrid,
        dataZoom: makeDataZoom(recs),
        xAxis: { type: "category", data: recs.map(r => r.draw_num), ...ECHARTS_THEME.xAxis, axisLabel: { ...ECHARTS_THEME.xAxis.axisLabel, rotate: 45 } },
        yAxis: { type: "value", ...ECHARTS_THEME.yAxis },
        series: [
          { name: "和值", type: "line", data: recs.map(r => r.sum_val), smooth: true, lineStyle: { color: "#58a6ff" }, itemStyle: { color: "#58a6ff" }, areaStyle: { color: "rgba(88,166,255,0.06)" } },
          { name: "跨度", type: "line", data: recs.map(r => r.span),    smooth: true, lineStyle: { color: "#3fb950" }, itemStyle: { color: "#3fb950" }, areaStyle: { color: "rgba(63,185,80,0.06)" } },
        ],
      });
    }
  } catch (e) { console.error(e); }

  try {
    const r = await fetch(`${API_BASE}/${currentType}/stats/ratio${dateParams}`).then(r => r.json());
    if (r.data && r.data.records) {
      const recs = r.data.records.reverse();
      const chart = echarts.init(rBox);
      chartInstances["extRatio"] = chart;
      addHelpBtn(rBox, "extRatio");
      chart.setOption({
        ...ECHARTS_THEME,
        title: { text: "奇偶比 / 大小比趋势", left: "center", top: 6, textStyle: { color: "#e6edf3", fontSize: 13 } },
        tooltip: { trigger: "axis", ...ECHARTS_THEME.tooltip },
        legend: { data: ["奇偶比(奇)", "大小比(大)"], top: 30, textStyle: { color: "#8b949e", fontSize: 11 } },
        grid: trendGrid,
        dataZoom: makeDataZoom(recs),
        xAxis: { type: "category", data: recs.map(r => r.draw_num), ...ECHARTS_THEME.xAxis, axisLabel: { ...ECHARTS_THEME.xAxis.axisLabel, rotate: 45 } },
        yAxis: { type: "value", ...ECHARTS_THEME.yAxis },
        series: [
          { name: "奇偶比(奇)", type: "line", data: recs.map(r => Number((r.odd_even_ratio || "0:0").split(":")[0])), smooth: true, lineStyle: { color: "#f85149" }, itemStyle: { color: "#f85149" }, areaStyle: { color: "rgba(248,81,73,0.06)" } },
          { name: "大小比(大)", type: "line", data: recs.map(r => Number((r.big_small_ratio || "0:0").split(":")[0])), smooth: true, lineStyle: { color: "#f0883e" }, itemStyle: { color: "#f0883e" }, areaStyle: { color: "rgba(240,136,62,0.06)" } },
        ],
      });
    }
  } catch (e) { console.error(e); }
}


// ── disposeAllCharts ──────────────────────────────────────────
function disposeAllCharts() {
  Object.keys(chartInstances).forEach(function(id) {
    if (chartInstances[id]) { chartInstances[id].dispose(); delete chartInstances[id]; }
  });
}

// ── 高级统计 ──────────────────────────────────────────────────
var advancedSubView = "scatter";

function loadAdvancedView() {
  var container = document.getElementById("advancedCharts");
  document.querySelectorAll("#advancedSubMenu .sub-btn").forEach(function(b){
    b.classList.toggle("active", b.dataset.advSub === advancedSubView);
  });
  disposeAllCharts();
  var dateParams = getDateParam();
  if (advancedSubView === "scatter") loadAdvScatter(container, dateParams);
  else if (advancedSubView === "lln") loadAdvLLN(container, dateParams);
  else loadAdvNormal(container, dateParams);
}

function initAdvancedSubMenu() {
  document.querySelectorAll("#advancedSubMenu .sub-btn").forEach(function(btn){
    btn.addEventListener("click", function(){
      advancedSubView = this.dataset.advSub;
      loadAdvancedView();
    });
  });
}

// ── 散点图 ──
function loadAdvScatter(container, dateParams) {
  var prefix = "/" + currentType;
  var sep = dateParams ? (dateParams + "&") : "?";
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div><div>加载中...</div></div>';
  fetch(API_BASE + prefix + "/stats/advanced/scatter" + sep + "limit=500")
    .then(function(r){return r.json();})
    .then(function(json){
      var data = json.data;
      if(!data||!data.positions){container.innerHTML='<div class="empty-state"><div class="empty-icon">📭</div><div class="empty-text">暂无数据</div></div>';return;}
      container.innerHTML="";
      Object.keys(data.positions).forEach(function(name){
        var points=data.positions[name];
        if(!points.length) return;
        var wrap=document.createElement("div");
        wrap.style.cssText="width:100%;min-height:280px;margin-bottom:16px;";
        var cid="chart-adv-scatter-"+name.replace(/\s/g,"");
        wrap.id=cid;container.appendChild(wrap);
        var chart=echarts.init(wrap);chartInstances[cid]=chart;
        chart.setOption({
          title:{text:name,left:"center",textStyle:{fontSize:13}},
          tooltip:{formatter:function(p){return "期数:"+p.data[0]+"<br>数值:"+p.data[1];}},
          grid:{left:50,right:20,top:35,bottom:40},
          xAxis:{type:"value",name:"期数序号"},
          yAxis:{type:"value",name:"号码值"},
          series:[{type:"scatter",data:points.map(function(p){return[p.index,p.value];}),symbolSize:4,itemStyle:{color:"#1890ff",opacity:0.6}}]
        });
      });
    }).catch(function(){container.innerHTML='<div class="empty-state"><div class="empty-text">网络错误</div></div>';});
}

// ── 大数定律 ──
function loadAdvLLN(container, dateParams) {
  var prefix="/"+currentType;
  var sep=dateParams?(dateParams+"&"):"?";
  container.innerHTML='<div class="loading-state"><div class="spinner"></div><div>加载中...</div></div>';
  fetch(API_BASE+prefix+"/stats/advanced/lln"+sep+"limit=500")
    .then(function(r){return r.json();})
    .then(function(json){
      var data=json.data;
      if(!data||!data.positions){container.innerHTML='<div class="empty-state"><div class="empty-text">暂无数据</div></div>';return;}
      container.innerHTML="";
      Object.keys(data.positions).forEach(function(name){
        var pts=data.positions[name];
        if(!pts.length) return;
        var wrap=document.createElement("div");
        wrap.style.cssText="width:100%;min-height:300px;margin-bottom:16px;";
        var cid="chart-adv-lln-"+name.replace(/\s/g,"");
        wrap.id=cid;container.appendChild(wrap);
        var chart=echarts.init(wrap);chartInstances[cid]=chart;
        var indices=pts.map(function(p){return p.index;});
        var avg=pts.map(function(p){return p.running_avg;});
        var l1=pts.map(function(p){return p.lower_1sigma;});
        var u1=pts.map(function(p){return p.upper_1sigma;});
        var l2=pts.map(function(p){return p.lower_2sigma;});
        var u2=pts.map(function(p){return p.upper_2sigma;});
        var exp=pts[0].expected_avg;
        var band1=indices.map(function(x,i){return[x,l1[i],u1[i]];});
        var band2=indices.map(function(x,i){return[x,l2[i],u2[i]];});
        chart.setOption({
          title:{text:name,left:"center",textStyle:{fontSize:13}},
          tooltip:{trigger:"axis"},
          legend:{bottom:0,data:["运行均值","理论均值","±1σ","±2σ"]},
          grid:{left:60,right:20,top:35,bottom:40},
          xAxis:{type:"value",name:"期数"},
          yAxis:{type:"value",name:"均值"},
          series:[
            {name:"±2σ",type:"line",data:band2,lineStyle:{opacity:0},areaStyle:{color:"rgba(24,144,255,0.06)"},symbol:"none",z:1},
            {name:"±1σ",type:"line",data:band1,lineStyle:{opacity:0},areaStyle:{color:"rgba(24,144,255,0.15)"},symbol:"none",z:2},
            {name:"运行均值",type:"line",data:indices.map(function(x,i){return[x,avg[i]];}),lineStyle:{color:"#1890ff",width:1.5},symbol:"none",z:3},
            {name:"理论均值",type:"line",data:[[indices[0],exp],[indices[indices.length-1],exp]],lineStyle:{color:"#ff4d4f",type:"dashed",width:1.5},symbol:"none",z:3}
          ]
        });
      });
    }).catch(function(){container.innerHTML='<div class="empty-state"><div class="empty-text">网络错误</div></div>';});
}

// ── 正态分布 ──
function loadAdvNormal(container, dateParams) {
  var prefix="/"+currentType;
  container.innerHTML='<div class="loading-state"><div class="spinner"></div><div>加载中...</div></div>';
  fetch(API_BASE+prefix+"/stats/advanced/normal"+(dateParams||""))
    .then(function(r){return r.json();})
    .then(function(json){
      var data=json.data;
      if(!data||!data.stats||!data.stats.length){container.innerHTML='<div class="empty-state"><div class="empty-text">暂无数据</div></div>';return;}
      container.innerHTML="";
      data.stats.forEach(function(st){
        if(!st.histogram||!st.histogram.bins||!st.histogram.bins.length) return;
        var wrap=document.createElement("div");
        wrap.style.cssText="width:100%;min-height:300px;margin-bottom:16px;";
        var cid="chart-adv-normal-"+st.field.replace(/\s/g,"");
        wrap.id=cid;container.appendChild(wrap);
        var chart=echarts.init(wrap);chartInstances[cid]=chart;
        var bins=st.histogram.bins,counts=st.histogram.counts,mean=st.mean,std=st.std;
        var curve=[];
        if(std>0){
          var xMin=bins[0],xMax=bins[bins.length-1],step=(xMax-xMin)/100;
          var total=counts.reduce(function(a,b){return a+b;},0);
          var binW=(xMax-xMin)/(bins.length||1);
          for(var x=xMin;x<=xMax;x+=step){
            var z=(x-mean)/std;
            curve.push([+x.toFixed(1),+total*binW*Math.exp(-0.5*z*z)/(std*Math.sqrt(2*Math.PI)).toFixed(2)]);
          }
        }
        chart.setOption({
          title:{text:st.field,left:"center",textStyle:{fontSize:13}},
          tooltip:{trigger:"axis"},
          grid:{left:60,right:20,top:35,bottom:40},
          xAxis:{type:"category",data:bins.map(String)},
          yAxis:{type:"value",name:"频次"},
          series:[
            {name:"频次",type:"bar",data:counts,barWidth:"60%",itemStyle:{color:"rgba(24,144,255,0.5)"}},
            {name:"正态拟合",type:"line",smooth:true,data:curve,lineStyle:{color:"#ff4d4f",width:2},symbol:"none"}
          ],
          graphic:[{type:"text",left:"center",bottom:8,style:{text:"μ="+mean+" σ="+std+" 偏度="+st.skewness+" 峰度="+st.kurtosis,fontSize:11,fill:"#999"}}]
        });
      });
    }).catch(function(){container.innerHTML='<div class="empty-state"><div class="empty-text">网络错误</div></div>';});
}
