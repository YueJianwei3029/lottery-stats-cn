# -*- coding: utf-8 -*-
"""定时调度模块：每次启动全量爬取，后续定时增量"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.config import CRAWL_INTERVAL_HOURS
from app.crawler import run_all_crawlers

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


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
    """启动定时调度：先全量爬取（表已由 init_database 重建为空），后续定时增量"""
    logger.info("[Scheduler] 启动时全量爬取...")
    crawl_job()

    scheduler.add_job(
        crawl_job,
        "interval",
        hours=CRAWL_INTERVAL_HOURS,
        id="crawl_job",
        replace_existing=True,
        next_run_time=None,
    )
    if not scheduler.running:
        scheduler.start()
    logger.info(f"[Scheduler] 已启动，间隔 {CRAWL_INTERVAL_HOURS} 小时")


def stop_scheduler():
    """停止调度"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] 已停止")
