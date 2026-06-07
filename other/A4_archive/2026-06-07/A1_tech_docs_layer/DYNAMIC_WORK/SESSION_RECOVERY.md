# 会话恢复文档（新对话入口）

> **用法**：新对话开始时，AI 读取本文档即可快速恢复项目上下文。

---

## 1. 项目速览

| 项目 | 说明 |
|------|------|
| 名称 | 彩票数据统计与可视化系统 |
| 目标 | 5 类彩票数据采集→清洗→存储→API→可视化 |
| 技术栈 | Python 3.13 + MySQL 8.0 + FastAPI + HTML/JS/ECharts + numpy + nginx |
| 本地环境 | Windows + PowerShell |
| 云域名 | www.yuejw.top |

## 2. 当前进度

| 阶段 | 状态 | 说明 |
|------|------|------|
| Phase 1~9 | ✅ | 基础设施→数据采集→API→前端→集成→Docker→云部署 |
| Phase 10 | ✅ | 前后端分离 + numpy加速 + 5彩种扩展统计 |
| **Phase 11** | ✅ | 路由工厂重构 + 高级统计（散点图/大数定律+正态置信带/正态分布） |

## 3. 架构

```
nginx:80 → /        → frontend/ 静态文件
         → /api/*   → app:8000 (FastAPI)
                       ├── router_factory (5配置→11端点/彩种)
                       └── MySQL:3306 (5张表)
```

- **Docker**：3 容器（mysql + app + nginx）
- **本地**：`start.bat`（FastAPI StaticFiles，无需 nginx）

### 3.1 API 端点（每彩种 11 个）

| 类别 | 端点 | 数量 |
|------|------|------|
| 通用 | `/query` `/stats` | 5×2 |
| 扩展 | `/stats/position` `/hot_cold` `/period_list` `/ratio` | 5×4 |
| 高级 | `/stats/advanced/std` `/percentile` `/normal` `/scatter` `/lln` | 5×5 |

### 3.2 前端 4 Tab

| Tab | 内容 |
|-----|------|
| 数据查询 | 日期区间分页 + 表格 |
| 基础统计 | 频率/奇偶/大小（3图表） |
| 扩展统计 | 分布分析（热力图+冷热号）/ 走势分析（和值跨度+奇偶比） |
| **高级统计** | 散点分布 / 大数定律(±1σ/±2σ置信带) / 正态分布(直方图+拟合曲线) |

### 3.3 数据库

| 表 | 记录数 |
|------|--------|
| lottery_dlt | 2,880 |
| lottery_7xc | 3,043 |
| lottery_ssq | 3,460 |
| lottery_pl5 | 7,620 |
| lottery_pl3 | 7,620 |

## 4. 项目结构

```
lottery_stats_cn/
├── app/
│   ├── main.py                    # FastAPI入口 + /api/health
│   ├── core/
│   │   ├── config.py              # DB/数据源/调度配置
│   │   ├── database.py            # MySQL连接/CRUD
│   │   ├── scheduler.py           # APScheduler 每24h采集
│   │   └── router_factory.py      # LotteryConfig + RouterFactory（替代5个路由文件）
│   ├── crawler/                   # 5个彩种采集器
│   ├── cleaner/                   # 数据清洗
│   ├── services/
│   │   ├── base_stats.py          # 通用统计(numpy)
│   │   ├── dlt_stats.py           # 大乐透扩展统计
│   │   ├── qxc_stats.py           # 七星彩扩展统计
│   │   ├── ssq_stats.py           # 双色球扩展统计
│   │   ├── pos_stats.py           # PL3/PL5共用扩展统计
│   │   └── advanced_stats.py      # 高级统计(scatter/lln/normal/std/percentile)
│   └── routers/                   # __init__.py only（路由由工厂生成）
├── frontend/
│   ├── index.html                 # 4Tab + 子菜单
│   ├── css/style.css
│   └── js/
│       ├── config.js              # API地址自动判断本地/云端
│       ├── app.js                 # 主逻辑
│       └── echarts.min.js
├── nginx/default.conf
├── docker-compose.yml
├── Dockerfile
├── requirements.txt               # numpy>=1.26.0
├── start.bat / start.ps1
└── other/                         # 文档体系(.gitignore排除)
    ├── A0_entry_layer/            # START.md / CONSTRAINT_LIST.md
    ├── A1_tech_docs_layer/        # 当前技术文档
    └── A4_archive/                # 历史归档(含废弃的随机性检验方案)
```

## 5. 环境信息

| 配置项 | 值 |
|--------|-----|
| 本地 MySQL | root / 123456 |
| 本地启动 | 双击 `start.bat` 或 `python -m uvicorn app.main:app --port 8000` |
| 前端地址 | `http://localhost:8000/frontend/index.html` |
| API 文档 | `http://localhost:8000/docs` |
| 云部署 | `git clone ... && docker compose up -d` |

## 6. 约束提醒

- 编码统一 UTF-8 无 BOM
- PowerShell 不支持 `&&` 串联，用 `;` 替代
- Git：`git push` → Gitee，`git push github master` → GitHub
- 扩展统计端点统一：position / hot_cold / period_list / ratio
- 高级统计端点：scatter / lln / normal / std / percentile
- 路由层：RouterFactory 配置驱动，5 个旧路由文件已删除
- A1S（STATIC_BASELINE）修改需用户确认
- A1D（DYNAMIC_WORK）AI 自由修改，每次告知用户

---

> **最后更新**: 2026-06-07 18:35
> **项目状态**: Phase 11 完成。路由工厂重构 + 高级统计（散点图/大数定律/正态分布）
