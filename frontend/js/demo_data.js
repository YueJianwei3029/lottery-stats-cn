// ==========================================
// 演示数据模块 — 模拟真实 API 响应
// 用于在没有后端时预览前端界面效果
// ==========================================

// ── 大乐透查询数据（20条） ──────────────────────────────────
const DEMO_QUERY_DLT = {
  data: {
    page: 1, page_size: 20, total: 856,
    records: [
      { id:1,  draw_num:"24001", draw_date:"2024-01-02", front_1:3,  front_2:10, front_3:19, front_4:26, front_5:33, back_1:5,  back_2:10 },
      { id:2,  draw_num:"24002", draw_date:"2024-01-06", front_1:1,  front_2:7,  front_3:14, front_4:22, front_5:30, back_1:3,  back_2:9  },
      { id:3,  draw_num:"24003", draw_date:"2024-01-09", front_1:6,  front_2:12, front_3:17, front_4:23, front_5:35, back_1:1,  back_2:8  },
      { id:4,  draw_num:"24004", draw_date:"2024-01-13", front_1:2,  front_2:8,  front_3:16, front_4:25, front_5:31, back_1:4,  back_2:11 },
      { id:5,  draw_num:"24005", draw_date:"2024-01-16", front_1:5,  front_2:11, front_3:20, front_4:28, front_5:34, back_1:2,  back_2:7  },
      { id:6,  draw_num:"24006", draw_date:"2024-01-20", front_1:4,  front_2:9,  front_3:18, front_4:27, front_5:32, back_1:6,  back_2:12 },
      { id:7,  draw_num:"24007", draw_date:"2024-01-23", front_1:7,  front_2:13, front_3:21, front_4:29, front_5:35, back_1:3,  back_2:10 },
      { id:8,  draw_num:"24008", draw_date:"2024-01-27", front_1:1,  front_2:6,  front_3:15, front_4:24, front_5:33, back_1:5,  back_2:9  },
      { id:9,  draw_num:"24009", draw_date:"2024-01-30", front_1:8,  front_2:14, front_3:22, front_4:30, front_5:35, back_1:1,  back_2:8  },
      { id:10, draw_num:"24010", draw_date:"2024-02-03", front_1:3,  front_2:11, front_3:16, front_4:25, front_5:34, back_1:4,  back_2:11 },
      { id:11, draw_num:"24011", draw_date:"2024-02-06", front_1:2,  front_2:10, front_3:19, front_4:28, front_5:32, back_1:2,  back_2:7  },
      { id:12, draw_num:"24012", draw_date:"2024-02-10", front_1:5,  front_2:13, front_3:20, front_4:27, front_5:31, back_1:6,  back_2:12 },
      { id:13, draw_num:"24013", draw_date:"2024-02-13", front_1:6,  front_2:9,  front_3:18, front_4:26, front_5:35, back_1:3,  back_2:10 },
      { id:14, draw_num:"24014", draw_date:"2024-02-17", front_1:4,  front_2:12, front_3:21, front_4:29, front_5:33, back_1:5,  back_2:9  },
      { id:15, draw_num:"24015", draw_date:"2024-02-20", front_1:7,  front_2:8,  front_3:17, front_4:24, front_5:30, back_1:1,  back_2:8  },
      { id:16, draw_num:"24016", draw_date:"2024-02-24", front_1:1,  front_2:14, front_3:22, front_4:25, front_5:34, back_1:4,  back_2:11 },
      { id:17, draw_num:"24017", draw_date:"2024-02-27", front_1:9,  front_2:11, front_3:16, front_4:23, front_5:32, back_1:2,  back_2:7  },
      { id:18, draw_num:"24018", draw_date:"2024-03-02", front_1:3,  front_2:7,  front_3:15, front_4:26, front_5:35, back_1:6,  back_2:12 },
      { id:19, draw_num:"24019", draw_date:"2024-03-05", front_1:10, front_2:13, front_3:19, front_4:28, front_5:31, back_1:3,  back_2:10 },
      { id:20, draw_num:"24020", draw_date:"2024-03-09", front_1:2,  front_2:6,  front_3:20, front_4:27, front_5:33, back_1:5,  back_2:9  }
    ]
  }
};

// ── 大乐透基础统计数据 ──────────────────────────────────────
const DEMO_STATS_DLT = {
  data: {
    fields: ["front_1","front_2","front_3","front_4","front_5","back_1","back_2"],
    freq: {
      front_1: {"1":48,"2":52,"3":61,"4":55,"5":58,"6":43,"7":47,"8":50,"9":54,"10":49,"11":53,"12":46,"13":51,"14":44,"15":56},
      front_2: {"8":42,"9":55,"10":48,"11":60,"12":53,"13":58,"14":45,"15":50,"16":65,"17":43,"18":57,"19":52,"20":49,"21":46,"22":54},
      front_3: {"14":38,"15":52,"16":48,"17":61,"18":55,"19":50,"20":58,"21":43,"22":53,"23":47,"24":62,"25":56,"26":41,"27":49,"28":44},
      front_4: {"20":35,"21":48,"22":55,"23":52,"24":60,"25":47,"26":58,"27":45,"28":53,"29":42,"30":50,"31":56,"32":41,"33":49,"34":63},
      front_5: {"27":30,"28":45,"29":53,"30":50,"31":48,"32":58,"33":62,"34":55,"35":70},
      back_1:  {"1":85,"2":78,"3":92,"4":81,"5":88,"6":75,"7":83,"8":79,"9":86,"10":73,"11":80,"12":69},
      back_2:  {"1":72,"2":83,"3":78,"4":88,"5":75,"6":91,"7":82,"8":77,"9":86,"10":73,"11":80,"12":93}
    },
    odd_even: {
      front_1: {"odd":312,"even":288},
      front_2: {"odd":298,"even":302},
      front_3: {"odd":321,"even":279},
      front_4: {"odd":285,"even":315},
      front_5: {"odd":334,"even":266},
      back_1:  {"odd":267,"even":333},
      back_2:  {"odd":311,"even":289}
    },
    big_small: {
      front_1: {"big":195,"small":405},
      front_2: {"big":278,"small":322},
      front_3: {"big":352,"small":248},
      front_4: {"big":398,"small":202},
      front_5: {"big":541,"small":59},
      back_1:  {"big":284,"small":316},
      back_2:  {"big":297,"small":303}
    }
  }
};

// ── 大乐透扩展统计 — 位置热力图 ────────────────────────────
const DEMO_POSITION_DLT = {
  data: {
    pos_front_1: {"1":48,"2":52,"3":61,"4":55,"5":58,"6":43,"7":47,"8":50,"9":54,"10":49,"11":53,"12":46,"13":51,"14":44,"15":56},
    pos_front_2: {"8":42,"9":55,"10":48,"11":60,"12":53,"13":58,"14":45,"15":50,"16":65,"17":43,"18":57,"19":52,"20":49,"21":46},
    pos_front_3: {"14":38,"15":52,"16":48,"17":61,"18":55,"19":50,"20":58,"21":43,"22":53,"23":47,"24":62,"25":56,"26":41,"27":49},
    pos_front_4: {"20":35,"21":48,"22":55,"23":52,"24":60,"25":47,"26":58,"27":45,"28":53,"29":42,"30":50,"31":56,"32":41,"33":49},
    pos_front_5: {"27":30,"28":45,"29":53,"30":50,"31":48,"32":58,"33":62,"34":55,"35":70},
    pos_back_1:  {"1":85,"2":78,"3":92,"4":81,"5":88,"6":75,"7":83,"8":79,"9":86,"10":73,"11":80,"12":69},
    pos_back_2:  {"1":72,"2":83,"3":78,"4":88,"5":75,"6":91,"7":82,"8":77,"9":86,"10":73,"11":80,"12":93}
  }
};

// ── 大乐透扩展统计 — 冷热号 ─────────────────────────────────
const DEMO_HOT_COLD_DLT = {
  data: {
    hot: [
      {number:"35",count:70},{number:"3",count:92},{number:"12",count:93},
      {number:"17",count:61},{number:"24",count:62},{number:"11",count:60},
      {number:"6",count:91},{number:"16",count:65},{number:"33",count:62},
      {number:"5",count:88}
    ],
    cold: [
      {number:"14",count:38},{number:"20",count:35},{number:"1",count:72},
      {number:"27",count:30},{number:"7",count:47},{number:"21",count:43},
      {number:"28",count:45},{number:"22",count:41},{number:"13",count:51},
      {number:"4",count:35}
    ]
  }
};

// ── 大乐透扩展统计 — 和值/跨度走势 ─────────────────────────
(function generatePeriodData() {
  var records = [];
  for (var i = 1; i <= 200; i++) {
    var nums = [];
    for (var j = 0; j < 5; j++) nums.push(Math.floor(Math.random() * 35) + 1);
    nums.sort(function(a, b) { return a - b; });
    var sum_val = nums.reduce(function(s, n) { return s + n; }, 0);
    var span = nums[4] - nums[0];
    records.push({
      draw_num: ("0000" + (23000 + i)).slice(-5),
      sum_val: sum_val,
      span: span
    });
  }
  window._DEMO_PERIOD = { data: { records: records } };
})();

// ── 大乐透扩展统计 — 奇偶比/大小比走势 ─────────────────────
(function generateRatioData() {
  var records = [];
  for (var i = 1; i <= 200; i++) {
    var nums = [];
    for (var j = 0; j < 5; j++) nums.push(Math.floor(Math.random() * 35) + 1);
    var odd = nums.filter(function(n) { return n % 2 !== 0; }).length;
    var big = nums.filter(function(n) { return n >= 18; }).length;
    records.push({
      draw_num: ("0000" + (23000 + i)).slice(-5),
      odd_even_ratio: odd + ":" + (5 - odd),
      big_small_ratio: big + ":" + (5 - big)
    });
  }
  window._DEMO_RATIO = { data: { records: records } };
})();

// ── Mock fetch ──────────────────────────────────────────────
// 拦截所有 API 请求，返回演示数据
var _originalFetch = window.fetch;
window.fetch = function(url, opts) {
  // 小延迟模拟网络请求
  return new Promise(function(resolve) {
    setTimeout(function() { resolve(); }, 300 + Math.random() * 200);
  }).then(function() {
    var u = String(url);

    if (u.includes("/stats/position")) return mockResponse(DEMO_POSITION_DLT);
    if (u.includes("/stats/hot_cold"))  return mockResponse(DEMO_HOT_COLD_DLT);
    if (u.includes("/stats/period_list")) return mockResponse(window._DEMO_PERIOD);
    if (u.includes("/stats/ratio"))     return mockResponse(window._DEMO_RATIO);
    if (u.includes("/stats"))           return mockResponse(DEMO_STATS_DLT);
    if (u.includes("/query"))           return mockResponse(DEMO_QUERY_DLT);

    // 其他走原始 fetch
    return _originalFetch(url, opts);
  });
};

function mockResponse(data) {
  return {
    ok: true,
    status: 200,
    json: function() { return Promise.resolve(data); }
  };
}

console.log(
  "%c\uD83C\uDFAF 演示模式已激活 — 所有 API 请求使用模拟数据",
  "color:#58a6ff;font-weight:bold;font-size:13px;"
);
