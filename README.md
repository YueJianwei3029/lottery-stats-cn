# 彩票数据统计与可视化系统

5 类彩票数据采集、清洗、存储、统计与可视化，支持 Docker 一键部署。

## 功能特性

- **5 种彩票**：超级大乐透、七星彩、双色球、排列5、排列3
- **数据查询**：按日期区间分页查询历史开奖数据
- **基础统计**：号码频率分布、奇偶分布、大小分布，按位置拆分
- **扩展统计**：大乐透（区间/和值/跨度）、七星彩（热力图/冷热号/012路/趋势）
- **定时采集**：每 24 小时自动增量更新数据
- **Docker 部署**：docker-compose 一键启动

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.13 + FastAPI |
| 数据库 | MySQL 8.0 |
| 前端 | HTML5 + JavaScript + ECharts 5 |
| 定时调度 | APScheduler |
| 数据源 | [乐彩网](https://data.17500.cn) 公开 TXT 数据 |
| 容器化 | Docker + Docker Compose |

## 快速开始（Docker）

```bash
# 1. 克隆项目
git clone https://gitee.com/yuejianwie/lottery-stats-cn.git
cd lottery_stats_cn

# 2. 设置数据库密码（可选，默认 lottery123）
cp .env.example .env
# 编辑 .env 修改密码

# 3. 启动
docker compose up -d

# 4. 等待首次数据爬取完成（约 2-3 分钟）
docker compose logs -f app

# 5. 访问
# 前端：http://localhost:8000/frontend/index.html
# API 文档：http://localhost:8000/docs
```

首次启动会自动清空数据库并全量爬取所有历史数据，之后每 24 小时增量更新。

## 本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 确保 MySQL 8.0 运行中，创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS lottery_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

# 3. 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. 访问 http://localhost:8000/frontend/index.html
```

可通过环境变量自定义数据库连接：

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
│   ├── main.py                 # FastAPI 入口
│   ├── core/
│   │   ├── config.py           # 配置（支持环境变量）
│   │   ├── database.py         # 数据库连接与 CRUD
│   │   └── scheduler.py        # 定时调度（首次全量 + 增量）
│   ├── crawler/                # 5 个彩种数据爬取器
│   ├── cleaner/                # 数据清洗与校验
│   ├── routers/                # 5 个彩种 API 路由
│   └── services/               # 统计分析服务
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js              # 主逻辑（三视图 + 图表渲染）
│       └── echarts.min.js      # ECharts 5.5
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API 文档

启动后访问 `http://localhost:8000/docs` 查看 Swagger UI。

## 数据来源

数据来自 [乐彩网](https://data.17500.cn) 公开的 TXT 格式开奖数据，仅供学习研究使用。

## 免责声明

本项目仅用于学习研究，**不提供任何投注建议**，不得用于赌博等非法用途。

## License

MIT License
