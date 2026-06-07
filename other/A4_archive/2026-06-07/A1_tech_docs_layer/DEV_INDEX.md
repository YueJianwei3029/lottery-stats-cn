# DEV_INDEX

> **文件地图**：记录所有文档和代码文件的路径与作用。

## 文档索引

| 文件路径 | 作用 |
|----------|------|
| `other/A0_entry_layer/START.md` | 项目入口，文档体系规则 |
| `other/A0_entry_layer/CONSTRAINT_LIST.md` | AI 行为约束 |
| `other/A0_entry_layer/DEV_NOTES.txt` | 用户开发笔记 |
| `other/A1_tech_docs_layer/DEV_INDEX.md` | 本文件，文件地图 |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/需求说明书.md` | 需求说明书（F-01~F-19） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/开发说明书.md` | 开发说明书（业务流程） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/系统架构.md` | 系统架构（Docker 3容器 + RouterFactory） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/数据设计.md` | 数据设计（5张表结构） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/接口设计.md` | 接口设计（55个端点） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/前端方案设计.md` | 前端方案（4Tab+子菜单） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/实现方案.md` | 实现方案（numpy算法 + RouterFactory） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/方案设计/任务分解.md` | 任务分解（从零搭建完整清单） |
| `other/A1_tech_docs_layer/STATIC_BASELINE/重构方案/09_路由工厂重构方案.md` | RouterFactory 重构设计 |
| `other/A1_tech_docs_layer/DYNAMIC_WORK/SESSION_RECOVERY.md` | 会话恢复文档 |
| `other/A4_archive/` | 历史归档（含废弃的随机性检验方案） |

## 代码索引

| 文件路径 | 作用 |
|----------|------|
| `app/main.py` | FastAPI 入口，路由注册，StaticFiles挂载，lifespan管理 |
| `app/core/config.py` | 项目配置（DB/数据源/调度24h/端口） |
| `app/core/database.py` | MySQL 连接、建库建表、CRUD |
| `app/core/scheduler.py` | APScheduler 每24h定时采集 |
| `app/core/router_factory.py` | 路由工厂（LotteryConfig + RouterFactory，替代旧5个路由文件） |
| `app/crawler/base_crawler.py` | 爬虫基类 |
| `app/crawler/pl3_crawler.py` | 排列3 爬虫 |
| `app/crawler/ssq_crawler.py` | 双色球 爬虫 |
| `app/crawler/pl5_crawler.py` | 排列5 爬虫 |
| `app/crawler/crawler_7xc.py` | 七星彩 爬虫 |
| `app/crawler/dlt_crawler.py` | 超级大乐透 爬虫 |
| `app/cleaner/base_cleaner.py` | 清洗基类 |
| `app/cleaner/pl3_cleaner.py` | 排列3 清洗器 |
| `app/cleaner/ssq_cleaner.py` | 双色球 清洗器 |
| `app/cleaner/pl5_cleaner.py` | 排列5 清洗器 |
| `app/cleaner/cleaner_7xc.py` | 七星彩 清洗器 |
| `app/cleaner/dlt_cleaner.py` | 超级大乐透 清洗器 |
| `app/services/base_stats.py` | 通用统计（numpy: 频率/奇偶/大小） |
| `app/services/dlt_stats.py` | 大乐透扩展统计（numpy: position/hot_cold/period_list/ratio） |
| `app/services/qxc_stats.py` | 七星彩扩展统计（numpy） |
| `app/services/ssq_stats.py` | 双色球扩展统计（numpy） |
| `app/services/pos_stats.py` | PL3+PL5 共用扩展统计（numpy） |
| `app/services/advanced_stats.py` | 高级统计（numpy: std/percentile/normal/scatter/lln） |
| `frontend/index.html` | 前端主页（4Tab + 子菜单） |
| `frontend/css/style.css` | 前端样式 |
| `frontend/js/config.js` | API 基地址配置（自动判断本地/云端） |
| `frontend/js/app.js` | 前端主逻辑（Tab切换/接口调用/ECharts渲染） |
| `frontend/js/echarts.min.js` | ECharts 5.5 |
| `nginx/default.conf` | nginx 反向代理 + 静态文件配置 |
| `Dockerfile` | 后端 Docker 镜像 |
| `docker-compose.yml` | 3容器编排（mysql + app + nginx） |
| `requirements.txt` | Python 依赖（numpy>=1.26.0） |
| `start.bat` / `start.ps1` | Windows 本地启动脚本 |
