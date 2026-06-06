# -*- coding: utf-8 -*-
"""定时调度模块：首次清库全量爬取，后续增量采集"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.config import CRAWL_INTERVAL_HOURS
from app.core.database import db
from app.crawler import run_all_crawlers

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

ALL_TABLES = ["lottery_dlt", "lottery_7xc", "lottery_ssq", "lottery_pl5", "lottery_pl3"]


def _is_first_run():
    """判断是否首次启动（所有表均为空）"""
    conn = db._connect()
    try:
        with conn.cursor() as cur:
            for table in ALL_TABLES:
                cur.execute(f"SELECT COUNT(*) FROM `{table}`")
                if cur.fetchone()[0] > 0:
                    return False
        return True
    except Exception:
        return False
    finally:
        conn.close()


def _truncate_keep_structure():
    """清空数据保留表结构（仅首次启动时使用）"""
    conn = db._connect()
    try:
        with conn.cursor() as cur:
            for table in ALL_TABLES:
                cur.execute(f"TRUNCATE TABLE `{table}`")
                logger.info(f"[Scheduler] 已清空表 {table}")
    finally:
        conn.close()


def crawl_job():
    """采集任务：遍历 5 个彩种，爬取 → 清洗 → 入库"""
    logger.info("[Scheduler] 开始执行采集任务...")
    try:
        results = run_all_crawlers()
        for table, count in results.items():
            logger.info(f"[Scheduler] {table}: 入库 {count} 条")
        logger.info("[Scheduler] 采集任务完成")
    except Exception as e:
        logger.error(f"[Scheduler] 采集任务异常: {e}")


def start_scheduler():
    """启动定时调度，首次运行清库全量爬取，后续定时增量"""
    if _is_first_run():
        logger.info("[Scheduler] 检测到首次启动，清空数据后全量爬取...")
        _truncate_keep_structure()
        # 首次全量爬取（同步执行，确保数据入库后再启动定时任务）
        crawl_job()

    scheduler.add_job(
        crawl_job,
        "interval",
        hours=CRAWL_INTERVAL_HOURS,
        id="crawl_job",
        replace_existing=True,
        next_run_time=None,  # 后续启动也立即跑一次增量
    )
    if not scheduler.running:
        scheduler.start()
    logger.info(f"[Scheduler] 已启动，间隔 {CRAWL_INTERVAL_HOURS} 小时")


def stop_scheduler():
    """停止调度"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] 已停止")
