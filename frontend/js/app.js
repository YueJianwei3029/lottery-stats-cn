// ==========================================
// 彩票数据统计与可视化系统 - 主逻辑
// ==========================================

const API_BASE = window.APP_CONFIG ? window.APP_CONFIG.API_BASE : "/api";
const HAS_EXTEND = { lottery_dlt: true, lottery_7xc: true, lottery_ssq: true, lottery_pl5: true, lottery_pl3: true };
let currentType = "lottery_dlt";
let currentPage = 1;
let totalPages = 1;
let currentPageSize = 10;
let currentTheme = (localStorage.getItem("lottery_theme") || "dark");
let chartInstances = {};
let currentView = "query";
let currentExtendSub = "dist";

// ── ECharts 主题（dark / light 双主题）─────
// dark：原深色配色（数据展示用）
// light：浅色配色（与 CSS 浅色变量对应）
const ECHARTS_DARK = {
    color: ["#58a6ff", "#f0883e", "#3fb950", "#f85149", "#bc8cff", "#39d9c8", "#e3b341", "#ff6b6b", "#79c0ff"],
    backgroundColor: "transparent",
    textStyle: { color: "#c9d1d9" },
    title: { textStyle: { color: "#e6edf3", fontSize: 14, fontWeight: 600 } },
    legend: {
        textStyle: { color: "#c9d1d9", fontSize: 12 },
        inactiveColor: "#484f58",
        pageTextStyle: { color: "#8b949e" },
    },
    tooltip: {
        backgroundColor: "rgba(13,17,23,0.96)",
        borderColor: "#30363d",
        textStyle: { color: "#e6edf3", fontSize: 12 },
    },
    categoryAxis: {
        axisLine: { lineStyle: { color: "#30363d" } },
        axisLabel: { color: "#c9d1d9", fontSize: 11 },
        axisTick: { lineStyle: { color: "#30363d" } },
        splitLine: { show: false },
        nameTextStyle: { color: "#c9d1d9", fontSize: 12 },
    },
    valueAxis: {
        axisLine: { show: false },
        axisLabel: { color: "#b0b8c4", fontSize: 10 },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: "#2a3a4d", type: "dashed" } },
        nameTextStyle: { color: "#b0b8c4", fontSize: 11 },
    },
    dataZoom: {
        textStyle: { color: "#b0b8c4" },
        dataBackground: {
            lineStyle: { color: "#c9d1d9", opacity: 0.3 },
            areaStyle: { color: "#c9d1d9", opacity: 0.05 },
        },
        selectedDataBackground: {
            lineStyle: { color: "#58a6ff", opacity: 0.5 },
            areaStyle: { color: "#58a6ff", opacity: 0.1 },
        },
    },
    visualMap: { textStyle: { color: "#b0b8c4" } },
};
echarts.registerTheme("dark", ECHARTS_DARK);

// light 主题：与 CSS 浅色变量对应
// 数据色：保持饱和度（蓝/橙/绿/红/紫/青/金/红橙/天蓝），但把偏亮色降饱和避免刺眼
const ECHARTS_LIGHT = {
    color: ["#0969da", "#bc4c00", "#1a7f37", "#cf222e", "#8250df", "#1b9e91", "#9a6700", "#d1242f", "#218bff"],
    backgroundColor: "transparent",
    textStyle: { color: "#1f2328" },
    title: { textStyle: { color: "#1f2328", fontSize: 14, fontWeight: 600 } },
    legend: {
        textStyle: { color: "#1f2328", fontSize: 12 },
        inactiveColor: "#afb8c1",
        pageTextStyle: { color: "#57606a" },
    },
    tooltip: {
        backgroundColor: "rgba(255,255,255,0.98)",
        borderColor: "#d0d7de",
        textStyle: { color: "#1f2328", fontSize: 12 },
    },
    categoryAxis: {
        axisLine: { lineStyle: { color: "#d0d7de" } },
        axisLabel: { color: "#1f2328", fontSize: 11 },
        axisTick: { lineStyle: { color: "#d0d7de" } },
        splitLine: { show: false },
        nameTextStyle: { color: "#1f2328", fontSize: 12 },
    },
    valueAxis: {
        axisLine: { show: false },
        axisLabel: { color: "#57606a", fontSize: 10 },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: "#eaeef2", type: "dashed" } },
        nameTextStyle: { color: "#57606a", fontSize: 11 },
    },
    dataZoom: {
        textStyle: { color: "#57606a" },
        dataBackground: {
            lineStyle: { color: "#57606a", opacity: 0.3 },
            areaStyle: { color: "#57606a", opacity: 0.05 },
        },
        selectedDataBackground: {
            lineStyle: { color: "#0969da", opacity: 0.5 },
            areaStyle: { color: "#0969da", opacity: 0.1 },
        },
    },
    visualMap: { textStyle: { color: "#57606a" } },
};
echarts.registerTheme("light", ECHARTS_LIGHT);

// 统一图表初始化（根据当前主题）
function initChart(dom) {
    return echarts.init(dom, currentTheme === "light" ? "light" : "dark");
}

// 主题相关色：按 currentTheme 返回硬编码色（给散落的 graphic / itemStyle / tooltip.formatter 用）
function themeColor(dark, light) {
    return currentTheme === "light" ? light : dark;
}

// ── 号码球颜色分类 ────────────────────────────────────
function getBallClass(key) {
    if (key === "draw_num") return "";
    if (key === "draw_date") return "";
    if (key.startsWith("front_")) return "ball-red";
    if (key.startsWith("back_")) return "ball-blue";
    if (key.startsWith("red_"))   return "ball-red";
    if (key === "blue_1")                return "ball-blue";
    if (key.startsWith("num_"))  return "ball-num";   // 排列三/五/七星彩：青色号码球
    if (key === "special_num")   return "ball-special";
    return "";
}

// ── 表格窄列分类 ──────────────────────────────────────
function getNarrowClass(key) {
    if (key === "id")       return "col-narrow col-id";
    if (key === "draw_num") return "col-narrow col-draw-num";
    if (key === "draw_date") return "col-narrow col-date";
    return "";
}

function div(cls, id, extraCls) {
    const d = document.createElement("div");
    d.className = cls + (extraCls ? " " + extraCls : "");
    if (id) d.id = id;
    return d;
}

// ========== 图表帮助 ==========
var CHART_HELP = {
    extHeat: { title: "位置×号码 热力图", text: "统计每个位置（纵轴）各个号码（横轴）在选定日期范围内的出现次数。<br><br><b>原理：</b>按日期范围筛选数据（默认全量），遍历所有期数，累计每个位置上各号码出现的频次。<br><br><b>读法：</b>颜色越深表示该位置该号码出现次数越多，可快速识别各位置的号码分布规律。<br><br><b>注：</b>各彩种号码范围不同（排列类0-9，双色球红球1-33，大乐透前区1-35），X轴范围会相应变化。" },
    extHotCold: { title: "冷热号", text: "统计选定日期范围内各号码的出现频次。<br><br><b>热号：</b>出现次数最多的号码（Top5~10），即高频号码。<br><b>冷号：</b>出现次数最少或从未出现的号码，即长期未出的号码。<br><br><b>原理：</b>按日期范围筛选数据，统计每个号码出现次数并按降序排列。若未指定日期，默认取最近50期；若指定了日期范围，则使用范围内全量数据。<br><br><b>读法：</b>左侧（红色）为热号，右侧（蓝色）为冷号。" },
    extPeriod: { title: "和值跨度走势", text: "逐期展示每期的号码之和与号码极差（最大值-最小值）。<br><br><b>和值：</b>当期所有号码相加的总和，反映号码整体的集中趋势。<br><b>跨度：</b>当期最大号码与最小号码的差值，反映号码的分散程度。<br><br><b>原理：</b>逐期计算和值与跨度，以折线图呈现变化趋势。若未指定日期，默认取最近500期；指定日期范围则使用范围内全量数据。可通过底部控件调整显示期数（20~200期）。" },
    extRatio: { title: "奇偶比/大小比趋势", text: "逐期展示每期奇数号码个数与偶数号码个数的比例，以及大号个数与小号个数的比例。<br><br><b>奇偶比：</b>奇数数量 : 偶数数量（如3:2表示3奇2偶）。<br><b>大小比：</b>大号数量 : 小号数量，分界值各彩种不同（排列类≥5为大，双色球红球≥17为大，大乐透前区≥18为大）。<br><br><b>原理：</b>逐期统计奇数/偶数个数和大号/小号个数，折线图展示趋势变化。若未指定日期，默认取最近500期。可通过底部控件调整显示期数（20~200期）。" },
};
function showChartHelp(key) {
    var h = CHART_HELP[key];
    if (!h) return;
    var overlay = document.createElement("div");
    overlay.className = "chart-help-overlay";
    overlay.innerHTML = '<div class="chart-help-dialog"><h3>📊 ' + h.title + '</h3><p>' + h.text + '</p><button class="help-close" onclick="this.closest(\'.chart-help-overlay\').remove()">关闭</button></div>';
    overlay.addEventListener("click", function(e) { if (e.target === overlay) overlay.remove(); });
    document.body.appendChild(overlay);
}
function addHelpBtn(box, key) {
    var btn = document.createElement("span");
    btn.className = "chart-tip";
    btn.title = "点击查看说明";
    btn.textContent = "?";
    btn.onclick = function(e) { e.stopPropagation(); showChartHelp(key); };
    box.appendChild(btn);
}

// 通用：添加一个右上角操作按钮（与 help 按钮并排）
// opts: { text, title, onClick, active }
//   active=true 时按钮显示"激活"样式（高亮）
function addChartActionBtn(box, opts) {
    var btn = document.createElement("span");
    btn.className = "chart-tip chart-action";
    if (opts.active) btn.classList.add("active");
    btn.title = opts.title || "";
    btn.textContent = opts.text || "•";
    btn.onclick = function(e) {
        e.stopPropagation();
        opts.onClick(btn);
    };
    box.appendChild(btn);
    return btn;
}

// ========== 初始化 ==========
document.addEventListener("DOMContentLoaded", () => {
    initNav();
    initViewToggle();
    initMobileNav();
    initMenuToggle();
    initThemeToggle();
    initControls();
    initPageSize();
    initExtendSubMenu();
    initAdvancedSubMenu();
    switchType(currentType);
});

// ========== 左侧彩种导航 ==========
function initNav() {
    document.querySelectorAll("#lotteryNav .nav-item").forEach(item => {
        item.addEventListener("click", () => {
            const type = item.dataset.type;
            if (type !== currentType) switchType(type);
        });
    });
}

function switchType(type) {
    currentType = type;
    currentPage = 1;

    document.querySelectorAll("#lotteryNav .nav-item").forEach(n =>
        n.classList.toggle("active", n.dataset.type === type)
    );

    disposeStatsCharts();
    loadQuery();

    if (currentView === "stats") loadStats();
    else if (currentView === "extend") loadExtendView();
    else if (currentView === "advanced") loadAdvancedView();
}

// ========== 视图切换（桌面端） ==========
function initViewToggle() {
    document.querySelectorAll(".view-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const view = btn.dataset.view;
            if (view !== currentView) switchToView(view);
        });
    });
}

// ========== 移动端底部导航 ==========
function initMobileNav() {
    document.querySelectorAll(".mobile-nav-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const view = btn.dataset.view;
            if (view === currentView) return;
            switchToView(view);
        });
    });
}

// 抽取视图切换的核心逻辑（桌面端 + 移动端共用）
function switchToView(view) {
    currentView = view;

    // 更新桌面端按钮
    document.querySelectorAll(".view-btn").forEach(b =>
        b.classList.toggle("active", b.dataset.view === view)
    );
    // 更新移动端按钮
    document.querySelectorAll(".mobile-nav-btn").forEach(b =>
        b.classList.toggle("active", b.dataset.view === view)
    );

    // 切换视图显示
    document.getElementById("viewQuery").classList.toggle("hidden", view !== "query");
    document.getElementById("viewStats").classList.toggle("hidden", view !== "stats");
    document.getElementById("viewExtend").classList.toggle("hidden", view !== "extend");
    document.getElementById("viewAdvanced").classList.toggle("hidden", view !== "advanced");

    // 加载对应视图数据
    if (view === "stats") loadStats();
    else if (view === "extend") loadExtendView();
    else if (view === "advanced") loadAdvancedView();
}

// ========== 汉堡菜单（移动端侧边栏） ==========
function initMenuToggle() {
    const toggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("lotteryNav");
    const overlay = document.getElementById("sidebarOverlay");
    if (!toggle || !sidebar || !overlay) return;

    toggle.addEventListener("click", () => {
        const isOpen = sidebar.classList.toggle("open");
        toggle.classList.toggle("open", isOpen);
        overlay.classList.toggle("show", isOpen);
    });

    overlay.addEventListener("click", () => {
        sidebar.classList.remove("open");
        toggle.classList.remove("open");
        overlay.classList.remove("show");
    });
}

// ========== 主题切换（dark / light） ==========
function initThemeToggle() {
    // 初始应用
    document.body.dataset.theme = currentTheme;

    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
        currentTheme = currentTheme === "dark" ? "light" : "dark";
        document.body.dataset.theme = currentTheme;
        localStorage.setItem("lottery_theme", currentTheme);
        // 销毁所有图表实例，等下一次渲染走新主题
        disposeCharts();
        rerenderAfterThemeChange();
    });
}

// ========== 主题切换工具 ==========
// 切换主题后必须清空 chartInstances 并重新渲染当前视图
// （ECharts 主题在 init 时锁定，dispose 是唯一干净的方式）
function rerenderAfterThemeChange() {
    if (currentView === "stats")      loadStats();
    else if (currentView === "extend") loadExtendView();
    else if (currentView === "advanced") loadAdvancedView();
}

// ========== 日期工具 ==========
function getDateParam() {
    const ds = document.getElementById("dateStart").value || "";
    const de = document.getElementById("dateEnd").value || "";
    const start = ds ? ds.replace(/-/g, "") : null;
    const end = de ? de.replace(/-/g, "") : null;
    const params = [];
    if (start) params.push(`date=${start}`);
    if (end) params.push(`end_date=${end}`);
    return params.length ? "?" + params.join("&") : "";
}

// ========== 增加页数选择 ==========
function initPageSize() {
    document.getElementById("pageSizeSelect").addEventListener("change", () => {
        currentPageSize = parseInt(document.getElementById("pageSizeSelect").value) || 10;
        currentPage = 1;
        loadQuery();
    });
}

// ========== 控件 ==========
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

function reloadCurrentView() {
    if (currentView === "stats") loadStats();
    else if (currentView === "extend") loadExtendView();
    else if (currentView === "advanced") loadAdvancedView();
}

// ========== 数据查询 ==========
async function loadQuery() {
    const tableLoading = document.getElementById("tableLoading");
    const tableEmpty = document.getElementById("tableEmpty");
    const table = document.getElementById("dataTable");

    tableLoading.style.display = "block";
    tableEmpty.style.display = "none";
    table.style.display = "none";

    const dateParams = getDateParam();
    const prefix = dateParams ? (dateParams + "&") : "?";
    const fullUrl = `${API_BASE}/${currentType}/query${prefix}page=${currentPage}&page_size=${currentPageSize}`;

    try {
        const resp = await fetch(fullUrl);
        const json = await resp.json();
        const data = json.data;
        console.log("[query]", currentType, "sample:", data.records && data.records[0]);

        if (!data || !data.records || data.records.length === 0) {
            tableLoading.style.display = "none";
            tableEmpty.style.display = "block";
            return;
        }

        renderTable(data.records);
        totalPages = Math.ceil(data.total / data.page_size) || 1;
        document.getElementById("pageInfo").textContent = data.page;
        document.getElementById("totalPagesEl").textContent = totalPages;
        document.getElementById("totalInfo").textContent = `共 ${data.total} 条`;
        document.getElementById("prevBtn").disabled = currentPage <= 1;
        document.getElementById("nextBtn").disabled = currentPage >= totalPages;
        table.style.display = "";
    } catch (e) {
        console.error("查询失败:", e);
    }
    tableLoading.style.display = "none";
}

// 按彩种生成 num_1..num_6 / back_1 等位次标签
// 七星彩特殊：6 个前区位 + 1 个后区位（后区字段名是 back_1 不是 num_7）
function buildNumLabels() {
    var posMap = {
        lottery_7xc: {
            num_1: "前1", num_2: "前2", num_3: "前3",
            num_4: "前4", num_5: "前5", num_6: "前6",
            back_1: "后区"
        },
        lottery_pl5: { num_1: "万位", num_2: "千位", num_3: "百位", num_4: "十位", num_5: "个位" },
        lottery_pl3: { num_1: "百位", num_2: "十位", num_3: "个位" },
    };
    var out = posMap[currentType];
    if (out) return out;
    // 默认：num_1..num_7 命名为"号码1-7"
    out = {};
    for (var i = 1; i <= 7; i++) out["num_" + i] = "号码" + i;
    return out;
}

// 按彩种隐藏的字段（小彩种无业务数据）
function getHiddenFields() {
    if (currentType === "lottery_7xc") {
        return ["sales_amount", "prize_pool"];
    }
    return [];
}

function renderTable(records) {
    if (!records.length) return;
    const hiddenFields = getHiddenFields();
    // 过滤掉要隐藏的字段
    const keys = Object.keys(records[0]).filter(k => !hiddenFields.includes(k));

    const numLabels = buildNumLabels();
    const FIELD_LABELS = {
        id: "序号", draw_num: "期号", draw_date: "开奖日期",
        num_1: numLabels.num_1 || "号码1",
        num_2: numLabels.num_2 || "号码2",
        num_3: numLabels.num_3 || "号码3",
        num_4: numLabels.num_4 || "号码4",
        num_5: numLabels.num_5 || "号码5",
        num_6: numLabels.num_6 || "号码6",
        num_7: numLabels.num_7 || "号码7",
        red_1: "红1", red_2: "红2", red_3: "红3", red_4: "红4", red_5: "红5", red_6: "红6",
        blue_1: "蓝球",
        front_1: "前1", front_2: "前2", front_3: "前3", front_4: "前4", front_5: "前5",
        back_1: numLabels.back_1 || "后1",
        back_2: "后2",
        special_num: "特别号",
        sales_amount: "销售额", prize_pool: "奖池",
    };

    const thead = document.getElementById("tableHead");
    thead.innerHTML = "<tr>" + keys.map(k => {
        var nc = getNarrowClass(k);
        return `<th class="${nc}">${FIELD_LABELS[k] || k}</th>`;
    }).join("") + "</tr>";
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

// ========== 基础统计 ==========
async function loadStats() {
    disposeStatsCharts();
    const container = document.getElementById("statsContainer");
    container.innerHTML = "";

    const dateParams = getDateParam();
    try {
        const resp = await fetch(`${API_BASE}/${currentType}/stats${dateParams}`);
        const json = await resp.json();
        const data = json.data;
        console.log("[stats]", currentType, "fields:", data && data.fields, "freq keys:", data && data.freq && Object.keys(data.freq));
        if (!data || !data.fields) {
            container.innerHTML = '<div class="empty-state"><div class="empty-text">暂无统计数据</div></div>';
            return;
        }

        const fields = data.fields;
        const labels = buildPosLabels(fields);

        if (currentType === "lottery_dlt") {
            buildDLTStats(container, data, fields, labels);
        } else if (currentType === "lottery_ssq") {
            buildSSQStats(container, data, fields, labels);
        } else {
            buildNormalStats(container, data, fields, labels);
        }
    } catch (e) {
        console.error("统计加载失败:", e);
        container.innerHTML = '<div class="empty-state"><div class="empty-text">统计加载失败，请检查后端服务</div></div>';
    }
}

function buildNormalStats(container, data, fields, labels) {
    // 七星彩：前区(6位) + 后区(1位) 拆成两个独立条形图
    if (currentType === "lottery_7xc") {
        const fFields = fields.filter(f => /^num_[1-6]$/.test(f));
        const bFields = fields.filter(f => f === "back_1");
        const fLabels = buildPosLabels(fFields);
        const bLabels = buildPosLabels(bFields);
        const fRange = buildFullRange(data.freq, fFields);
        const bRange = buildFullRange(data.freq, bFields);

        container.innerHTML = `
            <div class="stats-dlt">
                <div class="chart-full chart-box" id="chartFF"><span class="chart-tip" title="前区各位号码(0-9)出现次数">?</span></div>
                <div class="chart-full chart-box" id="chartBF"><span class="chart-tip" title="后区号码(0-14)出现次数">?</span></div>
                <div class="chart-half-row">
                    <div class="chart-box" id="chartOE"><span class="chart-tip" title="前后区奇偶分布">?</span></div>
                    <div class="chart-box" id="chartBS"><span class="chart-tip" title="前后区大小分布">?</span></div>
                </div>
            </div>`;
        renderGroupedBar("chartFF", { title: "前区号码频率 (0-9)", xData: fRange.map(String),
            series: fFields.map((f, i) => ({ name: fLabels[i], data: fRange.map(n => (data.freq[f] || {})[String(n)] || 0) })),
            xName: "号码", yName: "次数" });
        renderGroupedBar("chartBF", { title: "后区号码频率 (0-14)", xData: bRange.map(String),
            series: bFields.map((f, i) => ({ name: bLabels[i], data: bRange.map(n => (data.freq[f] || {})[String(n)] || 0) })),
            xName: "号码", yName: "次数" });
        renderStackedBar("chartOE", { title: "前后区奇偶分布", yData: labels,
            series: [{ name: "奇数", data: fields.map(f => (data.odd_even[f] || {}).odd || 0), color: "#e74c3c" },
                     { name: "偶数", data: fields.map(f => (data.odd_even[f] || {}).even || 0), color: "#3498db" }] });
        renderStackedBar("chartBS", { title: "前后区大小分布", yData: labels,
            series: [{ name: "大号", data: fields.map(f => (data.big_small[f] || {}).big || 0), color: "#fd7e14" },
                     { name: "小号", data: fields.map(f => (data.big_small[f] || {}).small || 0), color: "#20c997" }] });
        return;
    }

    const fullRange = buildFullRange(data.freq, fields);
    container.innerHTML = `
        <div class="stats-top"><div class="chart-box" id="chartFreq"><span class="chart-tip" title="各位置号码出现次数分布">?</span></div></div>
        <div class="stats-bottom">
            <div class="chart-box" id="chartOE"><span class="chart-tip" title="各位置奇偶号码分布">?</span></div>
            <div class="chart-box" id="chartBS"><span class="chart-tip" title="各位置大小号分布">?</span></div>
        </div>`;
    renderGroupedBar("chartFreq", { title: "各位置号码频率", xData: fullRange.map(String),
        series: fields.map((f, i) => ({ name: labels[i], data: fullRange.map(n => (data.freq[f]||{})[String(n)]||0) })),
        xName: "号码", yName: "次数" });
    renderStackedBar("chartOE", { title: "各位置奇偶分布", yData: labels,
        series: [{ name: "奇数", data: fields.map(f => (data.odd_even[f]||{}).odd||0), color: "#e74c3c" },
                 { name: "偶数", data: fields.map(f => (data.odd_even[f]||{}).even||0), color: "#3498db" }] });
    renderStackedBar("chartBS", { title: "各位置大小分布", yData: labels,
        series: [{ name: "大号", data: fields.map(f => (data.big_small[f]||{}).big||0), color: "#fd7e14" },
                 { name: "小号", data: fields.map(f => (data.big_small[f]||{}).small||0), color: "#20c997" }] });
}

function buildDLTStats(container, data, fields, labels) {
    const fFields = fields.filter(f => f.startsWith("front_"));
    const bFields = fields.filter(f => f.startsWith("back_"));
    const fLabels = buildPosLabels(fFields), bLabels = buildPosLabels(bFields);
    const fRange = buildFullRange(data.freq, fFields), bRange = buildFullRange(data.freq, bFields);

    container.innerHTML = `
        <div class="stats-dlt">
            <div class="chart-full chart-box" id="chartFF"><span class="chart-tip" title="前区(1-35)各位置号码出现次数">?</span></div>
            <div class="chart-full chart-box" id="chartBF"><span class="chart-tip" title="后区(1-12)各位置号码出现次数">?</span></div>
            <div class="chart-half-row">
                <div class="chart-box" id="chartOE"><span class="chart-tip" title="前后区各位置奇偶分布">?</span></div>
                <div class="chart-box" id="chartBS"><span class="chart-tip" title="前后区各位置大小分布">?</span></div>
            </div>
        </div>`;
    renderGroupedBar("chartFF", { title: "前区号码频率 (1-35)", xData: fRange.map(String),
        series: fFields.map((f,i) => ({ name: fLabels[i], data: fRange.map(n => (data.freq[f]||{})[String(n)]||0) })),
        xName: "号码", yName: "次数" });
    renderGroupedBar("chartBF", { title: "后区号码频率 (1-12)", xData: bRange.map(String),
        series: bFields.map((f,i) => ({ name: bLabels[i], data: bRange.map(n => (data.freq[f]||{})[String(n)]||0) })),
        xName: "号码", yName: "次数" });
    renderStackedBar("chartOE", { title: "前后区奇偶分布", yData: labels,
        series: [{ name: "奇数", data: fields.map(f => (data.odd_even[f]||{}).odd||0), color: "#e74c3c" },
                 { name: "偶数", data: fields.map(f => (data.odd_even[f]||{}).even||0), color: "#3498db" }] });
    renderStackedBar("chartBS", { title: "前后区大小分布", yData: labels,
        series: [{ name: "大号", data: fields.map(f => (data.big_small[f]||{}).big||0), color: "#fd7e14" },
                 { name: "小号", data: fields.map(f => (data.big_small[f]||{}).small||0), color: "#20c997" }] });
}

function buildSSQStats(container, data, fields, labels) {
    const redFields = fields.filter(f => f.startsWith("red_"));
    const blueFields = fields.filter(f => f.startsWith("blue_"));
    const redLabels = buildPosLabels(redFields), blueLabels = buildPosLabels(blueFields);
    const redRange = buildFullRange(data.freq, redFields), blueRange = buildFullRange(data.freq, blueFields);

    container.innerHTML = `
        <div class="stats-dlt">
            <div class="chart-full chart-box" id="chartRF"><span class="chart-tip" title="红球(1-33)各位置号码出现次数">?</span></div>
            <div class="chart-full chart-box" id="chartBF"><span class="chart-tip" title="蓝球(1-16)出现次数">?</span></div>
            <div class="chart-half-row">
                <div class="chart-box" id="chartOE"><span class="chart-tip" title="红球各位置奇偶分布">?</span></div>
                <div class="chart-box" id="chartBS"><span class="chart-tip" title="红球各位置大小分布(>=17为大)">?</span></div>
            </div>
        </div>`;
    renderGroupedBar("chartRF", { title: "红球号码频率 (1-33)", xData: redRange.map(String),
        series: redFields.map((f,i) => ({ name: redLabels[i], data: redRange.map(n => (data.freq[f]||{})[String(n)]||0) })),
        xName: "号码", yName: "次数" });
    renderChart("chartBF", { title: "蓝球频率 (1-16)", xData: blueRange.map(String),
        yData: blueRange.map(n => (data.freq[blueFields[0]]||{})[String(n)]||0),
        xName: "号码", yName: "次数", seriesName: "蓝球" });
    renderStackedBar("chartOE", { title: "红球奇偶分布", yData: redLabels,
        series: [{ name: "奇数", data: redFields.map(f => (data.odd_even[f]||{}).odd||0), color: "#e74c3c" },
                 { name: "偶数", data: redFields.map(f => (data.odd_even[f]||{}).even||0), color: "#3498db" }] });
    renderStackedBar("chartBS", { title: "红球大小分布", yData: redLabels,
        series: [{ name: "大号", data: redFields.map(f => (data.big_small[f]||{}).big||0), color: "#fd7e14" },
                 { name: "小号", data: redFields.map(f => (data.big_small[f]||{}).small||0), color: "#20c997" }] });
}

function buildPosLabels(fields) {
    var numLabels = buildNumLabels();
    // 大乐透/双色的字段优先级最高；七星彩的 num_*/back_1 用 numLabels
    var map = Object.assign({}, numLabels,
        { red_1:"红球1",red_2:"红球2",red_3:"红球3",red_4:"红球4",red_5:"红球5",red_6:"红球6",blue_1:"蓝球",
          front_1:"前区1",front_2:"前区2",front_3:"前区3",front_4:"前区4",front_5:"前区5",
          back_2:"后区2" });
    // back_1 若 numLabels 没给则用"后区1"兜底
    if (!map.back_1) map.back_1 = "后区1";
    return fields.map(f => map[f] || f);
}

// 热力图纵坐标标签 — 根据彩种类型映射
function buildHeatmapLabels(positions, lotType) {
    var MAPS = {
        lottery_dlt: ["前区1","前区2","前区3","前区4","前区5","后区1","后区2"],
        lottery_ssq: ["红球1","红球2","红球3","红球4","红球5","红球6","蓝球"],
        lottery_pl3: ["百位","十位","个位"],
        lottery_pl5: ["万位","千位","百位","十位","个位"],
        lottery_7xc: ["前1","前2","前3","前4","前5","前6","后区"],
    };
    var names = MAPS[lotType] || positions.map(function(p, i) { return "第" + (i+1) + "位"; });
    return positions.map(function(p, i) { return names[i] || p; });
}

// 单个位置名映射：用于散点图/LLN图标题替换"第X位"
function buildPosName(index, lotType) {
    var MAPS = {
        lottery_dlt: ["前区1","前区2","前区3","前区4","前区5","后区1","后区2"],
        lottery_ssq: ["红球1","红球2","红球3","红球4","红球5","红球6","蓝球"],
        lottery_pl3: ["百位","十位","个位"],
        lottery_pl5: ["万位","千位","百位","十位","个位"],
        lottery_7xc: ["前1","前2","前3","前4","前5","前6","后区"],
    };
    var names = MAPS[lotType];
    if (names && index < names.length) return names[index];
    return "第" + (index + 1) + "位";
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

function disposeStatsCharts() {
    Object.keys(chartInstances).forEach(id => {
        if (chartInstances[id]) { chartInstances[id].dispose(); delete chartInstances[id]; }
    });
}

// ========== 扩展统计视图（子菜单模式） ==========
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

    if (!HAS_EXTEND[currentType]) {
        container.innerHTML = `<div style="text-align:center;padding:60px 20px;color:#999;">
            <div style="font-size:48px;margin-bottom:16px;">&#x1f6a7;</div>
            <div style="font-size:16px;">功能正在开发中</div>
            <div style="font-size:13px;margin-top:8px;">当前彩种暂无扩展统计</div>
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
    if (currentExtendSub === "dist") {
        await loadDistCharts();
    } else {
        await loadTrendCharts();
    }
}

// ========== 子菜单1：分布分析（热力图 + 冷热号） ==========
async function loadDistCharts() {
    const extCharts = document.getElementById("extendCharts");
    if (!extCharts) return;
    extCharts.innerHTML = "";
    extCharts.className = "extend-layout";

    const dateParams = getDateParam();
    const isBig = currentType === "lottery_dlt" || currentType === "lottery_ssq";

    const heatRow = div("extend-row");
    const heatBox = div("chart-box", "extHeat", isBig ? "chart-full" : "");
    heatRow.appendChild(heatBox);
    extCharts.appendChild(heatRow);

    const hcRow = div("extend-row");
    const hcBox = div("chart-box", "extHotCold");
    hcRow.appendChild(hcBox);
    extCharts.appendChild(hcRow);

    // 热力图
    try {
        const r = await fetch(`${API_BASE}/${currentType}/stats/position${dateParams}`).then(r => r.json());
        if (r.data) {
            let positions = Object.keys(r.data);
            // 七星彩只统计前六位(pos_1~pos_6)，排除后区(pos_7)
            if (currentType === "lottery_7xc") {
                positions = positions.filter(p => /^pos_[1-6]$/.test(p));
            }
            const numSet = new Set();
            positions.forEach(p => Object.keys(r.data[p]).forEach(n => numSet.add(parseInt(n))));
            const numRange = Array.from(numSet).sort((a, b) => a - b);
            const heatData = [];
            // 计算最大频次，用于相对对比（去掉 0 的影响，让 0 之后的所有差异更明显）
            let maxV = 0;
            positions.forEach((p, pi) => {
                numRange.forEach((n, ni) => {
                    const v = r.data[p][String(n)] || 0;
                    heatData.push([ni, pi, v]);
                    if (v > maxV) maxV = v;
                });
            });
            // 相对对比：min 取一个略大于 0 的值（max 的 5%），避免 0 占满色阶
            const minV = maxV > 0 ? Math.max(1, maxV * 0.05) : 0;
            const hLabels = buildHeatmapLabels(positions, currentType);
            const chart = initChart(heatBox);
            chartInstances["extHeat"] = chart;
            addHelpBtn(heatBox, "extHeat");
            // "显示数字" 切换按钮：点击在每个热力格上显示/隐藏数值
            var heatShowNum = false;
            addChartActionBtn(heatBox, {
                text: "123",
                title: "点击切换显示数字",
                active: heatShowNum,
                onClick: function(btn) {
                    heatShowNum = !heatShowNum;
                    btn.classList.toggle("active", heatShowNum);
                    chart.setOption({
                        series: [{
                            type: "heatmap",
                            label: { show: heatShowNum, fontSize: 10, color: themeColor("#e6edf3", "#1f2328"), fontWeight: 600,
                                formatter: function(p) { return p.value[2] > 0 ? p.value[2] : ""; } },
                            itemStyle: { borderColor: themeColor("#0d1117", "#ffffff"), borderWidth: 1 },
                            emphasis: { label: { show: true, fontSize: 12, fontWeight: "bold" } }
                        }]
                    });
                }
            });
            var heatNames = buildAxisNameOptions("号码", "次数", { hasVisualMap: true, rotate: numRange.length > 20 });
            chart.setOption({
                title: { text: "位置x号码 热力图", left: "center", top: 4, textStyle: { fontSize: 14 } },
                tooltip: { formatter: function(p) { return hLabels[p.value[1]] + " · 号码" + numRange[p.value[0]] + "<br>出现 " + p.value[2] + " 次"; } },
                grid: { left: 85, right: 28, top: 40, bottom: 105, containLabel: true },
                xAxis: Object.assign({ type: "category", data: numRange.map(String),
                    axisLabel: { rotate: numRange.length > 20 ? 45 : 0, fontSize: 10,
                        interval: autoInterval(numRange.length), hideOverlap: true } }, heatNames.xAxis || {}),
                yAxis: Object.assign({ type: "category", data: hLabels }, heatNames.yAxis || {}),
                visualMap: { min: minV, max: maxV, calculable: true, orient: "horizontal", left: "center", bottom: 35,
                    // 红蓝双向渐变：低频=冷（蓝），高频=热（红），与冷热号语义对应
                    inRange: { color: currentTheme === "light"
                        ? ["#bfdbfe","#7dd3fc","#e5e7eb","#fcd34d","#fb923c","#f87171","#dc2626"]
                        : ["#1a3a5c","#1d6fa5","#7e9aa0","#e3b341","#f0883e","#e74c3c","#cf222e"] },
                    textStyle: { color: themeColor("#8b949e", "#57606a") } },
                series: [{ type: "heatmap", data: heatData, label: { show: false },
                    itemStyle: { borderColor: themeColor("#0d1117", "#ffffff"), borderWidth: 1 },
                    emphasis: { label: { show: true, fontSize: 12, fontWeight: "bold" } } }],
            });
        }
    } catch(e) { console.error(e); }

    // 冷热号
    try {
        const r = await fetch(`${API_BASE}/${currentType}/stats/hot_cold${dateParams}`).then(r => r.json());
        if (r.data) {
            // 七星彩前后区分开: {"front":{"hot":[...],"cold":[...]},"back":{"hot":[...],"cold":[...]}}
            // 只取前区
            let src = (currentType === "lottery_7xc" && r.data.front) ? r.data.front : r.data;
            let hot = (src.hot || []).reverse();
            let cold = (src.cold || []).reverse();
            const chart = initChart(hcBox);
            chartInstances["extHotCold"] = chart;
            addHelpBtn(hcBox, "extHotCold");
            chart.setOption({
                title: { text: "冷热号", left: "center", top: 4, textStyle: { fontSize: 14 } },
                tooltip: {},
                legend: { data: ["热号", "冷号"], top: 30 },
                grid: [{ left: "5%", top: 70, width: "40%", bottom: 50 }, { left: "55%", top: 70, width: "40%", bottom: 50 }],
                xAxis: [{ gridIndex: 0, type: "value" }, { gridIndex: 1, type: "value", inverse: true }],
                yAxis: [
                    { gridIndex: 0, type: "category", data: hot.map(h => h.number) },
                    { gridIndex: 1, type: "category", data: cold.map(c => c.number) },
                ],
                series: [
                    { name: "热号", type: "bar", data: hot.map(h => h.count), xAxisIndex: 0, yAxisIndex: 0, itemStyle: { color: "#e74c3c" } },
                    { name: "冷号", type: "bar", data: cold.map(c => c.count), xAxisIndex: 1, yAxisIndex: 1, itemStyle: { color: "#3498db" } },
                ],
            });
        }
    } catch(e) { console.error(e); }
}

// ========== 子菜单2：走势分析（和值跨度 + 奇偶比） ==========
async function loadTrendCharts() {
    const extCharts = document.getElementById("extendCharts");
    if (!extCharts) return;
    extCharts.innerHTML = "";
    extCharts.className = "extend-layout";

    const dateParams = getDateParam();

    const pRow = div("extend-row");
    const pBox = div("chart-box", "extPeriod");
    pRow.appendChild(pBox);
    extCharts.appendChild(pRow);

    const rRow = div("extend-row");
    const rBox = div("chart-box", "extRatio");
    rRow.appendChild(rBox);
    extCharts.appendChild(rRow);

    function makeDataZoom(recs) {
        var total = recs.length;
        if (total === 0) return [];
        // 默认显示最近 100 期（如果数据不足则全部显示），同时确保窗口能扩到全量，避免右边空一大截
        var window = Math.min(100, total);
        var sv = Math.max(0, total - window);
        // maxValueSpan 不能超过 total，否则右侧会留空
        var maxSpan = Math.max(20, total);
        return [
            { type: "slider", startValue: sv, endValue: total - 1, minValueSpan: 20, maxValueSpan: maxSpan, height: 20, bottom: 6 },
            { type: "inside", minValueSpan: 20, maxValueSpan: maxSpan },
        ];
    }
    var trendGrid = { left: 55, right: 28, top: 55, bottom: 95 };
    function trendXD(xd) { return { type: "category", data: xd, axisLabel: { rotate: 45, fontSize: 10, interval: "auto" } }; }

    try {
        var r = await fetch(API_BASE + "/" + currentType + "/stats/period_list" + dateParams).then(function(r) { return r.json(); });
        if (r.data && r.data.records) {
            var recs = r.data.records.reverse();
            var chart = initChart(pBox);
            chartInstances["extPeriod"] = chart;
            addHelpBtn(pBox, "extPeriod");
            var trendNames = buildAxisNameOptions("期号", "", { hasDataZoom: true });
            chart.setOption({
                title: { text: "和值跨度走势", left: "center", top: 4, textStyle: { fontSize: 14 } },
                tooltip: { trigger: "axis" },
                legend: { data: ["和值", "跨度"], top: 28 },
                grid: trendGrid,
                dataZoom: makeDataZoom(recs),
                xAxis: Object.assign({}, trendXD(recs.map(function(r) { return r.draw_num; })), trendNames.xAxis || {}),
                yAxis: Object.assign({ type: "value" }, trendNames.yAxis || {}),
                series: [
                    { name: "和值", type: "line", data: recs.map(function(r) { return r.sum_val; }), smooth: true },
                    { name: "跨度", type: "line", data: recs.map(function(r) { return r.span; }), smooth: true },
                ],
            });
        }
    } catch(e) { console.error(e); }

    try {
        var r = await fetch(API_BASE + "/" + currentType + "/stats/ratio" + dateParams).then(function(r) { return r.json(); });
        if (r.data && r.data.records) {
            var recs = r.data.records.reverse();
            var chart = initChart(rBox);
            chartInstances["extRatio"] = chart;
            addHelpBtn(rBox, "extRatio");
            var ratioNames = buildAxisNameOptions("期号", "", { hasDataZoom: true });
            chart.setOption({
                title: { text: "奇偶比/大小比趋势", left: "center", top: 4, textStyle: { fontSize: 14 } },
                tooltip: { trigger: "axis" },
                legend: { data: ["奇偶比(奇)", "大小比(大)"], top: 28 },
                grid: trendGrid,
                dataZoom: makeDataZoom(recs),
                xAxis: Object.assign({}, trendXD(recs.map(function(r) { return r.draw_num; })), ratioNames.xAxis || {}),
                yAxis: Object.assign({ type: "value" }, ratioNames.yAxis || {}),
                series: [
                    { name: "奇偶比(奇)", type: "line", data: recs.map(function(r) { return Number((r.odd_even_ratio || "0:0").split(":")[0]); }), smooth: true },
                    { name: "大小比(大)", type: "line", data: recs.map(function(r) { return Number((r.big_small_ratio || "0:0").split(":")[0]); }), smooth: true },
                ],
            });
        }
    } catch(e) { console.error(e); }
}


// ── 高级统计 ──────────────────────────────────────────────────
var advancedSubView = "scatter";

function loadAdvancedView() {
  // Clear only advanced chart instances
  Object.keys(chartInstances).forEach(function(id) {
    if (id.startsWith("adv-") && chartInstances[id]) {
      chartInstances[id].dispose(); delete chartInstances[id];
    }
  });
  var container = document.getElementById("advancedCharts");
  document.querySelectorAll("#advancedSubMenu .sub-btn").forEach(function(b){
    b.classList.toggle("active", b.dataset.advSub === advancedSubView);
  });
  var dateParams = getDateParam();
  if (advancedSubView === "scatter") loadAdvScatter(container, dateParams);
  else if (advancedSubView === "lln") loadAdvLLN(container, dateParams);
  // normal 已下线（2026-06-07 暂时移除正态分布功能）
}

function initAdvancedSubMenu() {
  document.querySelectorAll("#advancedSubMenu .sub-btn").forEach(function(btn){
    btn.addEventListener("click", function(){
      advancedSubView = this.dataset.advSub;
      loadAdvancedView();
    });
  });
}

function loadAdvScatter(container, dateParams) {
  var prefix = "/" + currentType;
  var sep = dateParams ? (dateParams + "&") : "?";
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div><div>加载中...</div></div>';
  fetch(API_BASE + prefix + "/stats/advanced/scatter" + sep + "limit=500")
    .then(function(r){return r.json();})
    .then(function(json){
      var data = json.data;
      if(!data||!data.positions){container.innerHTML='<div class="empty-state"><div class="empty-text">暂无数据</div></div>';return;}
      container.innerHTML="";
      Object.keys(data.positions).forEach(function(name, idx){
        var points=data.positions[name];
        if(!points.length) return;
        var wrap=document.createElement("div");
        wrap.style.cssText="width:100%;min-height:280px;margin-bottom:16px;";
        var cid="adv-scatter-"+name.replace(/\s/g,"");
        wrap.id=cid;container.appendChild(wrap);
        var chart=initChart(wrap);chartInstances[cid]=chart;
        var posTitle = buildPosName(idx, currentType);
        var scatterNames = buildAxisNameOptions("期数序号", "号码值");
        chart.setOption({
          title:{text:posTitle,left:"center",textStyle:{fontSize:13}},
          tooltip:{formatter:function(p){return "期数:"+p.data[0]+"<br>数值:"+p.data[1];}},
          // right 加大到 45，给"期数序号"/"期数"等右侧 axis.name 留空间，避免被裁
          grid:{left:60,right:28,top:35,bottom:60,containLabel:true},
          xAxis: Object.assign({type:"value"}, scatterNames.xAxis || {}),
          yAxis: Object.assign({type:"value"}, scatterNames.yAxis || {}),
          series:[{type:"scatter",data:points.map(function(p){return[p.index,p.value];}),symbolSize:5,itemStyle:{color: themeColor("#0d8a7c", "#0f766e"), opacity:0.9, borderColor: themeColor("#0d8a7c", "#0f766e"), borderWidth:0}}]
        });
      });
    }).catch(function(){container.innerHTML='<div class="empty-state"><div class="empty-text">网络错误</div></div>';});
}

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
      Object.keys(data.positions).forEach(function(name, idx){
        var pts=data.positions[name];
        if(!pts.length) return;
        var wrap=document.createElement("div");
        wrap.style.cssText="width:100%;min-height:300px;margin-bottom:16px;";
        var cid="adv-lln-"+name.replace(/\s/g,"");
        wrap.id=cid;container.appendChild(wrap);
        var chart=initChart(wrap);chartInstances[cid]=chart;
        var indices=pts.map(function(p){return p.index;});
        var avg=pts.map(function(p){return p.running_avg;});
        var l1=pts.map(function(p){return p.lower_1sigma;});
        var u1=pts.map(function(p){return p.upper_1sigma;});
        var l2=pts.map(function(p){return p.lower_2sigma;});
        var u2=pts.map(function(p){return p.upper_2sigma;});
        var exp=pts[0].expected_avg;
        var band1=indices.map(function(x,i){return[x,l1[i],u1[i]];});
        var band2=indices.map(function(x,i){return[x,l2[i],u2[i]];});
        var posTitle = buildPosName(idx, currentType);
        var llnNames = buildAxisNameOptions("期数", "均值");
        chart.setOption({
          title:{text:posTitle,left:"center",textStyle:{fontSize:13}},
          tooltip:{trigger:"axis"},
          legend:{bottom:0,data:["运行均值","理论均值","±1σ","±2σ"]},
          // right 加大到 45，给右侧"期数"轴名留空间
          grid:{left:60,right:28,top:35,bottom:60,containLabel:true},
          xAxis: Object.assign({type:"value"}, llnNames.xAxis || {}),
          yAxis: Object.assign({type:"value"}, llnNames.yAxis || {}),
          series:[
            {name:"±2σ",type:"line",data:band2,lineStyle:{opacity:0},areaStyle:{color: themeColor("rgba(88,166,255,0.05)", "rgba(9,105,218,0.06)")},symbol:"none",z:1},
            {name:"±1σ",type:"line",data:band1,lineStyle:{opacity:0},areaStyle:{color: themeColor("rgba(88,166,255,0.14)", "rgba(9,105,218,0.12)")},symbol:"none",z:2},
            {name:"运行均值",type:"line",data:indices.map(function(x,i){return[x,avg[i]];}),lineStyle:{color: themeColor("#58a6ff", "#0969da"), width:2.5},itemStyle:{color: themeColor("#58a6ff", "#0969da")},symbol:"none",z:4},
            {name:"理论均值",type:"line",data:[[indices[0],exp],[indices[indices.length-1],exp]],lineStyle:{color: themeColor("#f85149", "#cf222e"), type:"dashed", width:2},symbol:"none",z:3}
          ]
        });
      });
    }).catch(function(){container.innerHTML='<div class="empty-state"><div class="empty-text">网络错误</div></div>';});
}

// 正态分布：适配后端新结构
// loadAdvNormal 已下线（2026-06-07 暂时移除正态分布功能）
function loadAdvNormal(container, dateParams) {
  var prefix = "/" + currentType;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div><div>加载中...</div></div>';
  fetch(API_BASE + prefix + "/stats/advanced/normal" + (dateParams || ""))
    .then(function (r) { return r.json(); })
    .then(function (json) {
      var data = json.data;
      console.log("[normal] response:", data);
      // 不支持的彩种：data.type === null
      if (!data || !data.type) {
        container.innerHTML = '<div class="empty-state"><div class="empty-text">该彩种暂不支持正态分布分析（仅大乐透/双色球）</div></div>';
        return;
      }
      // 容错：兼容后端可能返回 bins 或 numbers
      var numbers = (data.histogram && (data.histogram.numbers || data.histogram.bins)) || [];
      var counts  = (data.histogram && data.histogram.counts) || [];
      // 当 type 有值但无任何号码数据时
      if (!numbers.length || !counts.length) {
        container.innerHTML = '<div class="empty-state"><div class="empty-text">暂无数据（期数=' + (data.total_periods || 0) + '）</div></div>';
        return;
      }

      container.innerHTML = "";
      var wrap = document.createElement("div");
      wrap.style.cssText = "width:100%;min-height:320px;margin-bottom:16px;";
      var cid = "adv-normal-" + data.type.replace(/[^a-z0-9]/gi, "");
      wrap.id = cid; container.appendChild(wrap);
      var chart = initChart(wrap); chartInstances[cid] = chart;

      // 理论参考线：均值 + ±1σ/±2σ（四条水平线）
      // 后端的 theoretical_curve.{x,y} 是 PDF 曲线（坐标系不匹配号码-频次图），改用水平参考线
      var ef = data.expected_freq, es = data.expected_std;
      var maxX = numbers.length;

      // 标题：type → 中文名
      var titleMap = {
        dlt_front: "大乐透前区号码正态分布",
        ssq_red:   "双色球红球正态分布",
      };
      var titleText = titleMap[data.type] || ("正态分布 " + data.type);

      // X 轴名按号码数量决定是否旋转
      var normalNames = buildAxisNameOptions("号码", "频次", { rotate: numbers.length > 20 });

      // 注解
      var ann = "期望频次=" + data.expected_freq
              + "  期望σ=" + data.expected_std
              + "  偏度=" + data.skewness
              + "  峰度=" + data.kurtosis
              + "  期数=" + data.total_periods
              + "  开奖数=" + data.total_draws;

      chart.setOption({
        title: { text: titleText, left: "center", textStyle: { fontSize: 13 } },
        tooltip: { trigger: "axis" },
        grid: { left: 60, right: 28, top: 35, bottom: numbers.length > 20 ? 90 : 70, containLabel: true },
        xAxis: Object.assign({
          type: "category",
          data: numbers.map(String),
          axisLabel: { rotate: numbers.length > 20 ? 45 : 0, fontSize: 10, interval: autoInterval(numbers.length), hideOverlap: true }
        }, normalNames.xAxis || {}),
        yAxis: Object.assign({ type: "value" }, normalNames.yAxis || {}),
        series: [
          {
            name: "实际频次",
            type: "bar",
            data: counts,
            barWidth: "60%",
            itemStyle: { color: themeColor("rgba(88,166,255,0.55)", "rgba(9,105,218,0.45)") }
          },
          {
            // 理论均值（水平线）—— 跨整个号码范围
            name: "期望频次",
            type: "line",
            data: [[0, ef], [maxX - 1, ef]],
            lineStyle: { color: themeColor("#f85149", "#cf222e"), width: 2, type: "dashed" },
            symbol: "none",
            markLine: { silent: true, symbol: "none" }
          },
          {
            // ±1σ 区间（水平线）—— 浅红虚线
            name: "±1σ",
            type: "line",
            data: [[0, ef - es], [maxX - 1, ef - es]],
            lineStyle: { color: themeColor("rgba(248,81,73,0.5)", "rgba(207,34,46,0.5)"), width: 1, type: "dotted" },
            symbol: "none"
          },
          {
            name: "+1σ",
            type: "line",
            data: [[0, ef + es], [maxX - 1, ef + es]],
            lineStyle: { color: themeColor("rgba(248,81,73,0.5)", "rgba(207,34,46,0.5)"), width: 1, type: "dotted" },
            symbol: "none"
          }
        ],
        graphic: [
          {
            type: "text", left: "center", bottom: numbers.length > 20 ? 4 : 8,
            style: { text: ann, fontSize: 11, fill: themeColor("#b0b8c4", "#57606a") }
          }
        ]
      });
    })
    .catch(function () {
      container.innerHTML = '<div class="empty-state"><div class="empty-text">网络错误</div></div>';
    });
}

// ========== 图表渲染工具 ==========

// 自适应 X 轴标签间隔：根据数据量计算 step，让号码铺满整个绘图区且不重叠
function autoInterval(n) {
    if (n <= 0) return 0;
    if (n <= 16)  return 0;            // 全部显示
    if (n <= 30)  return 1;            // 隔 1 显示
    if (n <= 50)  return 2;            // 隔 2
    if (n <= 80)  return 4;
    if (n <= 120) return 6;
    return Math.ceil(n / 20);
}

// 统一轴名：使用 ECharts 原生 axis.name + nameLocation='end'
// 这样"号码"会贴在 X 轴末端、"次数"贴在 Y 轴顶端，真正与坐标轴绑定
// 不再用 graphic，避免被 containLabel 裁切
// opts: { hasDataZoom, hasVisualMap, rotate } —— 透传给 grid 留空间
function buildAxisNameOptions(xName, yName, opts) {
    opts = opts || {};
    var rotate = !!opts.rotate;

    // 轴名样式：按主题返回（深色灰 / 浅色深灰）
    var nameTextStyle = { color: themeColor("#b0b8c4", "#57606a"), fontSize: 11, fontWeight: 400, padding: [0, 0, 0, 0] };

    var xAxis, yAxis;
    if (xName) {
        xAxis = {
            name: xName,
            nameLocation: "end",       // 贴在 X 轴末端（最右）
            nameGap: rotate ? 22 : 10, // 距轴标签的像素（够显示"期数"等 2-4 字即可，不留过多空白）
            nameTextStyle: nameTextStyle,
        };
    }
    if (yName) {
        yAxis = {
            name: yName,
            nameLocation: "end",       // 贴在 Y 轴顶端（最上）
            nameGap: 8,
            nameTextStyle: nameTextStyle,
        };
    }
    return { xAxis: xAxis, yAxis: yAxis };
}

// 通用柱状图
function renderChart(domId, opt) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = initChart(dom);
    chartInstances[domId] = chart;
    var n = opt.xData ? opt.xData.length : 0;
    var rotate = n > 20 ? 45 : 0;
    var xNameText = opt.xName || "";
    var yNameText = opt.yName || "";
    var names = buildAxisNameOptions(xNameText, yNameText, { rotate: rotate });
    chart.setOption({
        title: { text: opt.title, left: "center", textStyle: { fontSize: 14 } },
        tooltip: {},
        grid: { left: 60, right: 28, top: 55, bottom: rotate ? 90 : 70, containLabel: true },
        xAxis: Object.assign({ type: "category", data: opt.xData,
            axisLabel: { rotate: rotate, fontSize: 10, interval: autoInterval(n), hideOverlap: true } }, names.xAxis || {}),
        yAxis: Object.assign({ type: "value" }, names.yAxis || {}),
        series: [{ type: "bar", data: opt.yData, name: opt.seriesName || "", itemStyle: { color: themeColor("#1890ff", "#0969da") } }],
    });
}

// 饼图
function renderPie(domId, title, data) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = initChart(dom);
    chartInstances[domId] = chart;
    chart.setOption({
        title: { text: title, left: "center", textStyle: { fontSize: 14 } },
        tooltip: { trigger: "item" },
        legend: { bottom: 10 },
        series: [{
            type: "pie", radius: ["45%", "70%"], center: ["50%", "50%"],
            data: data,
            label: { formatter: "{b}: {c} ({d}%)" },
        }],
    });
}

// 仪表盘
function renderGauge(domId, title, avg, min, max) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = initChart(dom);
    chartInstances[domId] = chart;
    chart.setOption({
        title: { text: title, left: "center", textStyle: { fontSize: 14 } },
        series: [{
            type: "gauge",
            startAngle: 200, endAngle: -20,
            center: ["50%", "60%"], radius: "80%",
            min: min, max: max, splitNumber: 5,
            axisLine: { lineStyle: { width: 6, color: [[0.3, "#67e0e3"], [0.7, "#37a2da"], [1, "#fd666d"]] } },
            pointer: { length: "60%", width: 6, itemStyle: { color: "auto" } },
            axisTick: { distance: -5, length: 6, lineStyle: { width: 1 } },
            splitLine: { distance: -15, length: 14, lineStyle: { width: 2 } },
            axisLabel: { distance: -30, fontSize: 10 },
            detail: { valueAnimation: true, formatter: "{value}", fontSize: 28, offsetCenter: [0, "60%"] },
            data: [{ value: avg, name: `平均 ${avg}` }],
        }],
    });
}

// 分组柱状图
function renderGroupedBar(domId, opt) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = initChart(dom);
    chartInstances[domId] = chart;
    var n = opt.xData ? opt.xData.length : 0;
    var rotate = n > 20 ? 45 : 0;
    var xNameText = opt.xName || "";
    var yNameText = opt.yName || "";
    var names = buildAxisNameOptions(xNameText, yNameText, { rotate: rotate });
    chart.setOption({
        title: { text: opt.title, left: "center", textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis" },
        legend: { data: opt.series.map(s => s.name), bottom: 4, textStyle: { fontSize: 11 } },
        grid: { left: 65, right: 28, top: 55, bottom: rotate ? 95 : 75, containLabel: true },
        xAxis: Object.assign({ type: "category", data: opt.xData,
            axisLabel: { rotate: rotate, fontSize: 10, interval: autoInterval(n), hideOverlap: true } }, names.xAxis || {}),
        yAxis: Object.assign({ type: "value" }, names.yAxis || {}),
        series: opt.series.map(s => ({ type: "bar", name: s.name, data: s.data })),
    });
}

// 横向堆叠柱状图
function renderStackedBar(domId, opt) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = initChart(dom);
    chartInstances[domId] = chart;
    chart.setOption({
        title: { text: opt.title, left: "center", textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        legend: { data: opt.series.map(s => s.name), bottom: 4, textStyle: { fontSize: 11 } },
        grid: { left: 85, right: 20, top: 55, bottom: 65 },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: opt.yData },
        series: opt.series.map(s => ({
            type: "bar", stack: "total", name: s.name, data: s.data,
            itemStyle: s.color ? { color: s.color } : {},
            label: { show: true, formatter: p => p.value > 0 ? p.value : "" },
        })),
    });
}

// 销毁所有图表实例
function disposeCharts() {
    Object.values(chartInstances).forEach(c => c.dispose());
    chartInstances = {};
}
