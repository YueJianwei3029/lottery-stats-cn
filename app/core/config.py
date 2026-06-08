# -*- coding: utf-8 -*-
"""项目配置"""

import os

# ============================================================
# 数据库配置（环境变量优先，兼容 Docker / 本机开发）
# ============================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "charset": "utf8mb4",
    "autocommit": True,
}

DB_NAME = "lottery_db"

# ============================================================
# 数据源配置（公开彩票 TXT 数据 URL）
# 按实际数据源地址修改
# ============================================================
DATA_SOURCES = {
    "lottery_pl3": {
        "url": "https://data.17500.cn/pl3_asc.txt",
        "encoding": "utf-8",
    },
    "lottery_ssq": {
        "url": "https://data.17500.cn/ssq_asc.txt",
        "encoding": "utf-8",
    },
    "lottery_pl5": {
        "url": "https://data.17500.cn/pl5_asc.txt",
        "encoding": "utf-8",
    },
    "lottery_7xc": {
        "url": "https://data.17500.cn/7xc_asc.txt",
        "encoding": "utf-8",
    },
    "lottery_dlt": {
        "url": "https://data.17500.cn/dlt_asc.txt",
        "encoding": "utf-8",
    },
}

# ============================================================
# 调度配置
# ============================================================
# 采集间隔（小时），24 表示每天一次
CRAWL_INTERVAL_HOURS = 24

# ============================================================
# 服务配置
# ============================================================
API_HOST = "0.0.0.0"
API_PORT = 8000

# ============================================================
# 日志配置
# ============================================================
LOG_LEVEL = "INFO"
