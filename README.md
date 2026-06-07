# 彩票数据统计与可视化系统

> ⚠️ **声明**：本项目仅为数据分析与技术学习用途，所有数据来源于公开信息。**不提供任何投注建议，不鼓励也不支持任何形式的赌博行为。**

## 项目速览

| 项目 | 说明 |
|------|------|
| 名称 | 彩票数据统计与可视化系统 |
| 目标 | 5 类彩票公开数据：采集 → 清洗 → 存储 → API → 可视化 |
| 当前阶段 | **Phase 10 重构完成**（前后端分离 + numpy 加速 + 5 彩种扩展统计） |
| 本地 OS | Windows + PowerShell |
| 云域名 | www.yuejw.top |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.13 + FastAPI |
| 数据库 | MySQL 8.0 |
| 前端 | HTML5 + JavaScript + ECharts 5 |
| 统计加速 | numpy |
| 定时调度 | APScheduler |
| 反向代理 | nginx（Docker 生产模式） |
| 容器化 | Docker + Docker Compose（3 容器：mysql + app + nginx） |
| 数据来源 | 公开开奖数据 |

## 功能特性

- **5 种彩票**：超级大乐透、七星彩、双色球、排列5、排列3
- **数据查询**：按日期区间分页查询历史开奖数据
- **基础统计**：号码频率分布、奇偶分布、大小分布，按位置拆分
- **扩展统计**：全部 5 彩种均已补齐（热力图、冷热号、和值/跨度、奇偶比、012路、趋势图等 4 个标准端点）
- **高级统计**：后端已就绪（标准差/百分位/正态分布），前端占位待启用
- **定时采集**：每 24 小时自动增量更新
- **前端 4 Tab**：数据查询 / 基础统计 / 扩展统计 / 高级统计（🚧开发中）
- **图表交互**：dataZoom 滑块（20~200 期）、右上角 `?` 统计原理说明
- **API 基地址**：通过 `config.js` 自动切换本地/云端

## 架构

```
浏览器 ──→ nginx:80 ──→ 前端静态文件 (/)
                    └── /api/* 代理 ──→ app:8000 (FastAPI)
                                         └── MySQL:3306
```

- **Docker 生产**：3 容器编排，`docker compose up -d` 一键部署
- **本地开发**：`start.bat` 启动（FastAPI StaticFiles 直出，无需 nginx）

## 快速开始

### 云服务器部署（推荐）

```bash
git clone https://github.com/YueJianwei3029/lottery-stats-cn.git
cd lottery-stats-cn
echo "DB_PASSWORD=lottery123" > .env
docker compose down && docker compose up -d
# 访问 http://你的服务器IP 或 http://www.yuejw.top（需开放 80 端口）
```

### 本地 Docker

```bash
git clone https://github.com/YueJianwei3029/lottery-stats-cn.git  # 或 Gitee 镜像
cd lottery_stats_cn
cp .env.example .env
docker compose up -d
# 等待首次数据同步（约 2-3 分钟）
docker compose logs -f app
# 访问 http://localhost/frontend/index.html
# API 文档：http://localhost/docs
```

### 本地开发（无 Docker）

```bash
pip install -r requirements.txt
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS lottery_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
# 双击 start.bat 或手动启动：
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# 访问 http://localhost:8000/frontend/index.html
```

环境变量（可选）：

| 变量 | 默认值 |
|------|--------|
| DB_HOST | localhost |
| DB_PORT | 3306 |
| DB_USER | root |
| DB_PASSWORD | 123456 |

## 项目结构

```
lottery_stats_cn/
├── app/
│   ├── main.py                 # FastAPI入口 + /api/health
│   ├── core/                   # config / database / scheduler
│   ├── crawler/                # 5个彩种数据采集器
│   ├── cleaner/                # 数据清洗与校验
│   ├── routers/                # 5个彩种API路由（含扩展+高级端点）
│   └── services/
│       ├── base_stats.py       # 通用统计（numpy向量化）
│       ├── dlt_stats.py        # 大乐透扩展统计
│       ├── qxc_stats.py        # 七星彩扩展统计
│       ├── ssq_stats.py        # 双色球扩展统计
│       ├── pos_stats.py        # PL3/PL5 共用扩展统计
│       └── advanced_stats.py   # 高级统计（std/percentile/normal，后端已就绪）
├── frontend/
│   ├── index.html              # 4Tab + 子菜单
│   ├── css/style.css
│   └── js/
│       ├── config.js           # API基地址自动切换（本地/云端）
│       ├── app.js              # 主逻辑（视图切换 + 图表渲染）
│       └── echarts.min.js
├── nginx/
│   └── default.conf            # 反向代理配置
├── docker-compose.yml          # 3容器编排
├── Dockerfile
├── requirements.txt            # 含 numpy>=1.26.0
├── start.bat / start.ps1       # 本地一键启动脚本
```

## 数据库状态

| 表 | 记录数 |
|------|--------|
| lottery_dlt（大乐透） | ~2,880 |
| lottery_7xc（七星彩） | ~3,043 |
| lottery_ssq（双色球） | ~3,460 |
| lottery_pl5（排列5） | ~7,620 |
| lottery_pl3（排列3） | ~7,620 |

## API 文档

启动后访问 `/docs` 查看 Swagger UI。

## 开发约束

- 编码统一 UTF-8 无 BOM
- PowerShell 不支持 `&&` 串联，用 `;` 替代
- Git 多远程：`git push` → Gitee，`git push github master` → GitHub
- 扩展统计后端端点统一为：`position` / `hot_cold` / `period_list` / `ratio`

## 数据来源 & License

数据来自公开开奖信息，仅供学习研究使用。MIT License。
