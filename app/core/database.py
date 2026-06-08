# -*- coding: utf-8 -*-
"""数据库模块：建库建表、连接管理、CRUD"""

import os
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
            num_1 TINYINT NOT NULL COMMENT '前区1(0-9)',
            num_2 TINYINT NOT NULL COMMENT '前区2(0-9)',
            num_3 TINYINT NOT NULL COMMENT '前区3(0-9)',
            num_4 TINYINT NOT NULL COMMENT '前区4(0-9)',
            num_5 TINYINT NOT NULL COMMENT '前区5(0-9)',
            num_6 TINYINT NOT NULL COMMENT '前区6(0-9)',
            back_1 TINYINT NOT NULL COMMENT '后区(0-14)',
            sales_amount DECIMAL(15,2) DEFAULT NULL COMMENT '销量',
            prize_pool DECIMAL(15,2) DEFAULT NULL COMMENT '奖池',
            INDEX idx_draw_date (draw_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='七星彩';
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

    # ---------- 表名校验 ----------
    @staticmethod
    def _validate_table(table: str):
        """白名单校验表名，防止 SQL 注入"""
        if table not in CREATE_TABLE_SQL:
            raise ValueError(f"Invalid table name: {table}")

    # ---------- 日期序列化 ----------
    @staticmethod
    def _serialize_records(records: list):
        """将记录中的 date/datetime 对象转为 ISO 字符串"""
        for r in records:
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()

    # ---------- 初始化 ----------
    def init_database(self, mode=None):
        """初始化数据库

        mode:
          - "rebuild"：删表重建（开发模式，数据由爬虫全量采集）
          - "ensure"：仅确保表存在，不删除数据（生产模式）
        """
        mode = mode or os.getenv("INIT_MODE", "ensure")
        if mode == "rebuild":
            logger.info("[DB] 初始化数据库（删表重建模式）...")
        else:
            logger.info("[DB] 初始化数据库（确保表存在模式）...")
        self._ensure_db()
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                for table_name, sql in CREATE_TABLE_SQL.items():
                    if mode == "rebuild":
                        cur.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                        cur.execute(sql)
                        logger.info(f"[DB] 表 {table_name} 已重建")
                    else:
                        cur.execute(sql)
                        logger.info(f"[DB] 表 {table_name} 已确认存在")
        finally:
            conn.close()
        logger.info("[DB] 数据库初始化完成")

    # ---------- 查询 ----------
    def query(self, table: str, date: str = None, end_date: str = None, page: int = 1, page_size: int = 20) -> dict:
        """分页查询，支持日期区间"""
        self._validate_table(table)
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
                self._serialize_records(records)
                return {"total": total, "page": page, "page_size": page_size, "records": records}
        finally:
            conn.close()

    def fetch_all(self, table: str, date: str = None, end_date: str = None) -> list:
        """获取全表数据（统计用），支持日期区间"""
        self._validate_table(table)
        conn = self._connect()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                where_clause, where_params = _build_date_where(date, end_date)
                cur.execute(f"SELECT * FROM `{table}` {where_clause} ORDER BY draw_num DESC", where_params)
                records = cur.fetchall()
                self._serialize_records(records)
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

        self._validate_table(table)
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
