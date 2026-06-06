# -*- coding: utf-8 -*-
"""数据库模块：建库建表、连接管理、CRUD"""

import pymysql
import logging
from app.core.config import DB_CONFIG, DB_NAME

logger = logging.getLogger(__name__)

# ============================================================
# 建表 SQL（严格遵循数据设计文档）
# ============================================================
CREATE_TABLE_SQL = {
    "lottery_pl3": """
        CREATE TABLE IF NOT EXISTS lottery_pl3 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_num VARCHAR(10) NOT NULL UNIQUE COMMENT '期号',
            draw_date DATE NOT NULL COMMENT '开奖日期',
            num_1 TINYINT NOT NULL COMMENT '百位',
            num_2 TINYINT NOT NULL COMMENT '十位',
            num_3 TINYINT NOT NULL COMMENT '个位',
            INDEX idx_draw_date (draw_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='排列3';
    """,
    "lottery_ssq": """
        CREATE TABLE IF NOT EXISTS lottery_ssq (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_num VARCHAR(10) NOT NULL UNIQUE COMMENT '期号',
            draw_date DATE NOT NULL COMMENT '开奖日期',
            red_1 TINYINT NOT NULL COMMENT '红球1',
            red_2 TINYINT NOT NULL COMMENT '红球2',
            red_3 TINYINT NOT NULL COMMENT '红球3',
            red_4 TINYINT NOT NULL COMMENT '红球4',
            red_5 TINYINT NOT NULL COMMENT '红球5',
            red_6 TINYINT NOT NULL COMMENT '红球6',
            blue_1 TINYINT NOT NULL COMMENT '蓝球',
            INDEX idx_draw_date (draw_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='双色球';
    """,
    "lottery_pl5": """
        CREATE TABLE IF NOT EXISTS lottery_pl5 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_num VARCHAR(10) NOT NULL UNIQUE COMMENT '期号',
            draw_date DATE NOT NULL COMMENT '开奖日期',
            num_1 TINYINT NOT NULL COMMENT '万位',
            num_2 TINYINT NOT NULL COMMENT '千位',
            num_3 TINYINT NOT NULL COMMENT '百位',
            num_4 TINYINT NOT NULL COMMENT '十位',
            num_5 TINYINT NOT NULL COMMENT '个位',
            INDEX idx_draw_date (draw_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='排列5';
    """,
    "lottery_7xc": """
        CREATE TABLE IF NOT EXISTS lottery_7xc (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_num VARCHAR(10) NOT NULL UNIQUE COMMENT '期号',
            draw_date DATE NOT NULL COMMENT '开奖日期',
            num_1 TINYINT NOT NULL COMMENT '基本号码1',
            num_2 TINYINT NOT NULL COMMENT '基本号码2',
            num_3 TINYINT NOT NULL COMMENT '基本号码3',
            num_4 TINYINT NOT NULL COMMENT '基本号码4',
            num_5 TINYINT NOT NULL COMMENT '基本号码5',
            num_6 TINYINT NOT NULL COMMENT '基本号码6',
            num_7 TINYINT NOT NULL COMMENT '基本号码7',
            sales_amount DECIMAL(15,2) DEFAULT NULL COMMENT '销量',
            prize_pool DECIMAL(15,2) DEFAULT NULL COMMENT '奖池',
            INDEX idx_draw_date (draw_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='七乐彩';
    """,
    "lottery_dlt": """
        CREATE TABLE IF NOT EXISTS lottery_dlt (
            id INT AUTO_INCREMENT PRIMARY KEY,
            draw_num VARCHAR(10) NOT NULL UNIQUE COMMENT '期号',
            draw_date DATE NOT NULL COMMENT '开奖日期',
            front_1 TINYINT NOT NULL COMMENT '前区号码1',
            front_2 TINYINT NOT NULL COMMENT '前区号码2',
            front_3 TINYINT NOT NULL COMMENT '前区号码3',
            front_4 TINYINT NOT NULL COMMENT '前区号码4',
            front_5 TINYINT NOT NULL COMMENT '前区号码5',
            back_1 TINYINT NOT NULL COMMENT '后区号码1',
            back_2 TINYINT NOT NULL COMMENT '后区号码2',
            INDEX idx_draw_date (draw_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='超级大乐透';
    """,
}


def _fmt_date(d: str) -> str:
    """YYYYMMDD → YYYY-MM-DD"""
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if d else ""


def _build_date_where(date: str = None, end_date: str = None):
    """构造日期 WHERE 子句和参数"""
    conditions = []
    params = []
    if date:
        conditions.append("draw_date >= %s")
        params.append(_fmt_date(date))
    if end_date:
        conditions.append("draw_date <= %s")
        params.append(_fmt_date(end_date))
    if conditions:
        return "WHERE " + " AND ".join(conditions), params
    return "", []


class Database:
    """MySQL 数据库操作封装（每次操作独立连接，线程安全）"""

    def __init__(self):
        pass

    # ---------- 连接 ----------
    def _connect(self):
        """创建新连接（已选库）"""
        conn = pymysql.connect(**{**DB_CONFIG, "database": DB_NAME})
        return conn

    def _connect_no_db(self):
        """创建新连接（未选库，用于建库）"""
        return pymysql.connect(**DB_CONFIG)

    def _ensure_db(self):
        """确保数据库存在"""
        conn = self._connect_no_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                    f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
        finally:
            conn.close()

    # ---------- 初始化 ----------
    def init_database(self):
        """首次启动：创建数据库 + 5 张表（IF NOT EXISTS 幂等安全）"""
        logger.info("[DB] 初始化数据库...")
        self._ensure_db()
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                for table_name, sql in CREATE_TABLE_SQL.items():
                    cur.execute(sql)
                    logger.info(f"[DB] 表 {table_name} 就绪")
        finally:
            conn.close()
        logger.info("[DB] 数据库初始化完成")

    # ---------- 查询 ----------
    def query(self, table: str, date: str = None, end_date: str = None, page: int = 1, page_size: int = 20) -> dict:
        """分页查询，支持日期区间"""
        conn = self._connect()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                where_clause, where_params = _build_date_where(date, end_date)

                cur.execute(f"SELECT COUNT(*) AS cnt FROM `{table}` {where_clause}", where_params)
                total = cur.fetchone()["cnt"]

                offset = (page - 1) * page_size
                cur.execute(
                    f"SELECT * FROM `{table}` {where_clause} "
                    f"ORDER BY draw_num DESC LIMIT %s OFFSET %s",
                    where_params + [page_size, offset],
                )
                records = cur.fetchall()

                for r in records:
                    for k, v in r.items():
                        if hasattr(v, "isoformat"):
                            r[k] = v.isoformat()

                return {"total": total, "page": page, "page_size": page_size, "records": records}
        finally:
            conn.close()

    def fetch_all(self, table: str, date: str = None, end_date: str = None) -> list:
        """获取全表数据（统计用），支持日期区间"""
        conn = self._connect()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                where_clause, where_params = _build_date_where(date, end_date)
                cur.execute(f"SELECT * FROM `{table}` {where_clause} ORDER BY draw_num DESC", where_params)
                records = cur.fetchall()
                for r in records:
                    for k, v in r.items():
                        if hasattr(v, "isoformat"):
                            r[k] = v.isoformat()
                return records
        finally:
            conn.close()

    # ---------- 写入 ----------
    def batch_insert(self, table: str, records: list) -> int:
        """
        批量 INSERT IGNORE，按期号去重，返回实际插入行数

        :param table: 表名
        :param records: list[dict]，key 为字段名
        :return: 实际插入行数
        """
        if not records:
            return 0

        conn = self._connect()
        try:
            columns = list(records[0].keys())
            placeholders = ", ".join(["%s"] * len(columns))
            col_names = ", ".join(f"`{c}`" for c in columns)

            sql = f"INSERT IGNORE INTO `{table}` ({col_names}) VALUES ({placeholders})"

            values = []
            for r in records:
                values.append([r[c] for c in columns])

            with conn.cursor() as cur:
                cur.executemany(sql, values)
                inserted = cur.rowcount

            logger.info(f"[DB] {table}: 本次 {len(records)} 条, 新增 {inserted} 条")
            return inserted
        finally:
            conn.close()


# 全局单例
db = Database()
