// ==========================================
// 彩票数据统计与可视化系统 - 主逻辑
// ==========================================

const API_BASE = "/api";
const HAS_EXTEND = { lottery_dlt: true, lottery_7xc: true };
let currentType = "lottery_dlt";
let currentPage = 1;
let totalPages = 1;
let currentPageSize = 20;
let chartInstances = {};
let currentView = "query";

// ========== 初始化 ==========
document.addEventListener("DOMContentLoaded", () => {
    initNav();
    initViewToggle();
    initControls();
    initPageSize();
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
}

// ========== 视图切换 ==========
function initViewToggle() {
    document.querySelectorAll(".view-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const view = btn.dataset.view;
            if (view === currentView) return;
            currentView = view;

            document.querySelectorAll(".view-btn").forEach(b =>
                b.classList.toggle("active", b.dataset.view === view)
            );

            document.getElementById("viewQuery").style.display = view === "query" ? "block" : "none";
            document.getElementById("viewStats").style.display = view === "stats" ? "block" : "none";
            document.getElementById("viewExtend").style.display = view === "extend" ? "block" : "none";

            if (view === "stats") loadStats();
            else if (view === "extend") loadExtendView();
        });
    });
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
        currentPageSize = parseInt(document.getElementById("pageSizeSelect").value) || 20;
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

        if (!data || !data.records || data.records.length === 0) {
            tableLoading.style.display = "none";
            tableEmpty.style.display = "block";
            return;
        }

        renderTable(data.records);
        totalPages = Math.ceil(data.total / data.page_size) || 1;
        document.getElementById("pageInfo").textContent = `第 ${data.page} / ${totalPages} 页`;
        document.getElementById("totalInfo").textContent = `共 ${data.total} 条`;
        document.getElementById("prevBtn").disabled = currentPage <= 1;
        document.getElementById("nextBtn").disabled = currentPage >= totalPages;
        table.style.display = "";
    } catch (e) {
        console.error("查询失败:", e);
    }
    tableLoading.style.display = "none";
}

function renderTable(records) {
    if (!records.length) return;
    const keys = Object.keys(records[0]);

    const FIELD_LABELS = {
        id: "序号", draw_num: "期号", draw_date: "开奖日期",
        num_1: "号码1", num_2: "号码2", num_3: "号码3", num_4: "号码4", num_5: "号码5",
        red_1: "红1", red_2: "红2", red_3: "红3", red_4: "红4", red_5: "红5", red_6: "红6",
        blue_1: "蓝球",
        front_1: "前1", front_2: "前2", front_3: "前3", front_4: "前4", front_5: "前5",
        back_1: "后1", back_2: "后2",
        num_6: "号码6", num_7: "号码7",
        special_num: "特别号",
        sales_amount: "销售额", prize_pool: "奖池",
    };

    const thead = document.getElementById("tableHead");
    thead.innerHTML = "<tr>" + keys.map(k => `<th>${FIELD_LABELS[k] || k}</th>`).join("") + "</tr>";
    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = records.map(r =>
        "<tr>" + keys.map(k => `<td>${r[k] !== null ? r[k] : "-"}</td>`).join("") + "</tr>"
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
        if (!data || !data.fields) return;

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
    }
}

function buildNormalStats(container, data, fields, labels) {
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
    const map = { num_1:"位置1",num_2:"位置2",num_3:"位置3",num_4:"位置4",num_5:"位置5",num_6:"位置6",num_7:"位置7",
        red_1:"红球1",red_2:"红球2",red_3:"红球3",red_4:"红球4",red_5:"红球5",red_6:"红球6",blue_1:"蓝球",
        front_1:"前区1",front_2:"前区2",front_3:"前区3",front_4:"前区4",front_5:"前区5",
        back_1:"后区1",back_2:"后区2" };
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

function disposeStatsCharts() {
    Object.keys(chartInstances).forEach(id => {
        if (chartInstances[id]) { chartInstances[id].dispose(); delete chartInstances[id]; }
    });
}

// ========== 扩展统计视图（独立页面） ==========
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

    container.innerHTML = '<div class="charts-grid" id="extendCharts"></div>';
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
    if (currentType === "lottery_dlt") {
        await loadDltExtend();
    } else if (currentType === "lottery_7xc") {
        await loadQxcExtend();
    }
}

async function loadDltExtend() {
    const extCharts = document.getElementById("extendCharts");
    if (!extCharts) return;
    ["extArea", "extZone", "extSum", "extSpan"].forEach(id => {
        const div = document.createElement("div");
        div.className = "chart-box";
        div.id = id;
        extCharts.appendChild(div);
    });

    const dateParams = getDateParam();

    try {
        const r1 = await fetch(`${API_BASE}/lottery_dlt/stats/area${dateParams}`).then(r => r.json());
        if (r1.data) {
            const fa = r1.data.front_area || {};
            renderChart("extArea", {
                title: "前区/后区频率", type: "bar",
                xData: Object.keys(fa), yData: Object.values(fa),
                seriesName: "前区", xName: "号码", yName: "次",
            });
        }
    } catch(e) { console.error(e); }

    try {
        const r2 = await fetch(`${API_BASE}/lottery_dlt/stats/zone${dateParams}`).then(r => r.json());
        if (r2.data) {
            const names = Object.keys(r2.data);
            renderChart("extZone", {
                title: "5区间分布", type: "bar",
                xData: names.map(k => r2.data[k].range), yData: names.map(k => r2.data[k].count),
                xName: "区间", yName: "次",
            });
        }
    } catch(e) { console.error(e); }

    try {
        const r3 = await fetch(`${API_BASE}/lottery_dlt/stats/sum_span${dateParams}`).then(r => r.json());
        if (r3.data) {
            renderGauge("extSum", "前区和值", r3.data.sum_avg, r3.data.sum_min, r3.data.sum_max);
            renderGauge("extSpan", "前区跨度", r3.data.span_avg, r3.data.span_min, r3.data.span_max);
        }
    } catch(e) { console.error(e); }
}

async function loadQxcExtend() {
    const extCharts = document.getElementById("extendCharts");
    if (!extCharts) return;
    ["extPos", "extDigit", "extHotCold", "extRatio", "extRoad", "extTrend"].forEach(id => {
        const div = document.createElement("div");
        div.className = "chart-box";
        div.id = id;
        extCharts.appendChild(div);
    });

    const dateParams = getDateParam();

    try {
        const r1 = await fetch(`${API_BASE}/lottery_7xc/stats/position${dateParams}`).then(r => r.json());
        if (r1.data) {
            const positions = Object.keys(r1.data);
            const numRange = [];
            for (let n = 1; n <= 9; n++) numRange.push(n);
            const extraNums = new Set();
            positions.forEach(p => Object.keys(r1.data[p]).forEach(n => {
                const v = parseInt(n);
                if (v > 9 && (r1.data[p][n] || 0) > 5) extraNums.add(v);
            }));
            [...extraNums].sort((a, b) => a - b).forEach(n => numRange.push(n));

            const heatData = [];
            positions.forEach((p, pi) => {
                numRange.forEach((n, ni) => {
                    heatData.push([ni, pi, r1.data[p][String(n)] || 0]);
                });
            });

            const dom = document.getElementById("extPos");
            if (dom) {
                const chart = echarts.init(dom);
                chartInstances["extPos"] = chart;
                chart.setOption({
                    title: { text: "各位置号码频率热力图" },
                    tooltip: {},
                    grid: { left: 60, right: 20, top: 50, bottom: 50 },
                    xAxis: { type: "category", data: numRange.map(String), name: "号码" },
                    yAxis: { type: "category", data: positions.map(p => p.replace("pos_", "位置")), name: "位置" },
                    visualMap: { min: 0, calculable: true, orient: "horizontal", left: "center", bottom: 0 },
                    series: [{
                        type: "heatmap", data: heatData, label: { show: true },
                        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: "rgba(0,0,0,0.5)" } },
                    }],
                });
            }
        }
    } catch(e) { console.error(e); }

    try {
        const r2 = await fetch(`${API_BASE}/lottery_7xc/stats/digit_freq${dateParams}`).then(r => r.json());
        if (r2.data && r2.data.digit_freq) {
            const d = r2.data.digit_freq;
            renderChart("extDigit", {
                title: "0-9数字频率", type: "bar",
                xData: Object.keys(d), yData: Object.values(d),
                xName: "数字", yName: "次",
            });
        }
    } catch(e) { console.error(e); }

    try {
        const r3 = await fetch(`${API_BASE}/lottery_7xc/stats/hot_cold${dateParams}`).then(r => r.json());
        if (r3.data) {
            const hot = (r3.data.hot || []).reverse();
            const cold = (r3.data.cold || []).reverse();
            const dom = document.getElementById("extHotCold");
            if (dom) {
                const chart = echarts.init(dom);
                chartInstances["extHotCold"] = chart;
                chart.setOption({
                    title: { text: "冷热号 Top5" },
                    tooltip: {},
                    legend: { data: ["热号", "冷号"] },
                    grid: [{ left: "5%", top: 60, width: "40%" }, { left: "55%", top: 60, width: "40%" }],
                    xAxis: [{ gridIndex: 0, type: "value" }, { gridIndex: 1, type: "value", inverse: true }],
                    yAxis: [
                        { gridIndex: 0, type: "category", data: hot.map(h => "号码" + h.number) },
                        { gridIndex: 1, type: "category", data: cold.map(c => "号码" + c.number) },
                    ],
                    series: [
                        { name: "热号", type: "bar", data: hot.map(h => h.count), xAxisIndex: 0, yAxisIndex: 0, itemStyle: { color: "#e74c3c" } },
                        { name: "冷号", type: "bar", data: cold.map(c => c.count), xAxisIndex: 1, yAxisIndex: 1, itemStyle: { color: "#3498db" } },
                    ],
                });
            }
        }
    } catch(e) { console.error(e); }

    try {
        const r4 = await fetch(`${API_BASE}/lottery_7xc/stats/ratio${dateParams}`).then(r => r.json());
        if (r4.data && r4.data.records) {
            const recs = r4.data.records.slice(0, 50).reverse();
            const dom = document.getElementById("extRatio");
            if (dom) {
                const chart = echarts.init(dom);
                chartInstances["extRatio"] = chart;
                chart.setOption({
                    title: { text: "奇偶比/大小比趋势" },
                    tooltip: { trigger: "axis" },
                    legend: { data: ["奇偶比(奇)", "大小比(大)"] },
                    xAxis: { type: "category", data: recs.map(r => r.draw_num) },
                    yAxis: { type: "value", min: 0, max: 7 },
                    series: [
                        { name: "奇偶比(奇)", type: "line", data: recs.map(r => Number((r.odd_even_ratio || "0:0").split(":")[0])) },
                        { name: "大小比(大)", type: "line", data: recs.map(r => Number((r.big_small_ratio || "0:0").split(":")[0])) },
                    ],
                });
            }
        }
    } catch(e) { console.error(e); }

    try {
        const r5 = await fetch(`${API_BASE}/lottery_7xc/stats/ratio${dateParams}`).then(r => r.json());
        if (r5.data && r5.data.records && r5.data.records.length) {
            const latest = (r5.data.records[0] || {}).road_012 || {};
            renderPie("extRoad", "最新期012路分布", [
                { name: "0路", value: latest["0"] || 0 },
                { name: "1路", value: latest["1"] || 0 },
                { name: "2路", value: latest["2"] || 0 },
            ]);
        }
    } catch(e) { console.error(e); }

    try {
        const r6 = await fetch(`${API_BASE}/lottery_7xc/stats/trend${dateParams}`).then(r => r.json());
        if (r6.data && r6.data.records) {
            const recs = r6.data.records.slice(0, 50).reverse();
            const dom = document.getElementById("extTrend");
            if (dom) {
                const chart = echarts.init(dom);
                chartInstances["extTrend"] = chart;
                chart.setOption({
                    title: { text: "销量/奖池趋势" },
                    tooltip: { trigger: "axis" },
                    legend: { data: ["销量", "奖池"] },
                    xAxis: { type: "category", data: recs.map(r => r.draw_num) },
                    yAxis: { type: "value" },
                    series: [
                        { name: "销量", type: "line", data: recs.map(r => r.sales_amount), connectNulls: true },
                        { name: "奖池", type: "line", data: recs.map(r => r.prize_pool), connectNulls: true },
                    ],
                });
            }
        }
    } catch(e) { console.error(e); }
}

// ========== 图表渲染工具 ==========
function renderChart(domId, opt) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = echarts.init(dom);
    chartInstances[domId] = chart;
    chart.setOption({
        title: { text: opt.title, left: "center", textStyle: { fontSize: 14 } },
        tooltip: {},
        grid: { left: 50, right: 20, top: 50, bottom: 40 },
        xAxis: { type: "category", data: opt.xData, name: opt.xName || "", axisLabel: { rotate: opt.xData && opt.xData.length > 20 ? 45 : 0 } },
        yAxis: { type: "value", name: opt.yName || "" },
        series: [{ type: "bar", data: opt.yData, name: opt.seriesName || "", itemStyle: { color: "#1a73e8" } }],
    });
}

function renderPie(domId, title, data) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = echarts.init(dom);
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

function renderGauge(domId, title, avg, min, max) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = echarts.init(dom);
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
    const chart = echarts.init(dom);
    chartInstances[domId] = chart;
    const rotate = opt.xData.length > 20 ? 45 : 0;
    chart.setOption({
        title: { text: opt.title, left: "center", textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis" },
        legend: { data: opt.series.map(s => s.name), bottom: 4, textStyle: { fontSize: 11 } },
        grid: { left: 50, right: 20, top: 50, bottom: 50 },
        xAxis: { type: "category", data: opt.xData, name: opt.xName || "", axisLabel: { rotate } },
        yAxis: { type: "value", name: opt.yName || "" },
        series: opt.series.map(s => ({ type: "bar", name: s.name, data: s.data })),
    });
}

// 横向堆叠柱状图
function renderStackedBar(domId, opt) {
    const dom = document.getElementById(domId);
    if (!dom) return;
    if (chartInstances[domId]) chartInstances[domId].dispose();
    const chart = echarts.init(dom);
    chartInstances[domId] = chart;
    chart.setOption({
        title: { text: opt.title, left: "center", textStyle: { fontSize: 14 } },
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        legend: { data: opt.series.map(s => s.name), bottom: 4, textStyle: { fontSize: 11 } },
        grid: { left: 80, right: 20, top: 50, bottom: 50 },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: opt.yData },
        series: opt.series.map(s => ({
            type: "bar", stack: "total", name: s.name, data: s.data,
            itemStyle: s.color ? { color: s.color } : {},
            label: { show: true, formatter: p => p.value > 0 ? p.value : "" },
        })),
    });
}

function disposeCharts() {
    Object.values(chartInstances).forEach(c => c.dispose());
    chartInstances = {};
}
