# -*- coding: utf-8 -*-
"""爬虫模块入口：统一调用 5 个彩种爬虫"""

import time
import logging
from app.crawler.pl3_crawler import Pl3Crawler
from app.crawler.ssq_crawler import SsqCrawler
from app.crawler.pl5_crawler import Pl5Crawler
from app.crawler.crawler_7xc import QxcCrawler
from app.crawler.dlt_crawler import DltCrawler
from app.cleaner.pl3_cleaner import Pl3Cleaner
from app.cleaner.ssq_cleaner import SsqCleaner
from app.cleaner.pl5_cleaner import Pl5Cleaner
from app.cleaner.cleaner_7xc import QxcCleaner
from app.cleaner.dlt_cleaner import DltCleaner
from app.core.database import db

logger = logging.getLogger(__name__)

# 请求间隔（秒），避免 429 限流
CRAWL_DELAY = 3

# 彩种注册表
LOTTERY_REGISTRY = {
    "lottery_pl3": {"crawler": Pl3Crawler, "cleaner": Pl3Cleaner},
    "lottery_ssq": {"crawler": SsqCrawler, "cleaner": SsqCleaner},
    "lottery_pl5": {"crawler": Pl5Crawler, "cleaner": Pl5Cleaner},
    "lottery_7xc": {"crawler": QxcCrawler, "cleaner": QxcCleaner},
    "lottery_dlt": {"crawler": DltCrawler, "cleaner": DltCleaner},
}


def run_all_crawlers() -> dict:
    """执行全部采集任务，返回各表入库行数"""
    results = {}
    tables = list(LOTTERY_REGISTRY.items())
    for i, (table, cls) in enumerate(tables):
        try:
            if i > 0:
                logger.info(f"[Crawler] 等待 {CRAWL_DELAY}s 避免限流...")
                time.sleep(CRAWL_DELAY)

            crawler = cls["crawler"]()
            cleaner = cls["cleaner"]()
            raw_text = crawler.fetch()
            if not raw_text:
                logger.warning(f"[Crawler] {table}: 数据为空，跳过")
                results[table] = 0
                continue
            records = cleaner.parse(raw_text)
            if not records:
                logger.warning(f"[Crawler] {table}: 解析无结果，跳过")
                results[table] = 0
                continue
            inserted = db.batch_insert(table, records)
            results[table] = inserted
        except Exception as e:
            logger.error(f"[Crawler] {table}: 异常 {e}")
            results[table] = 0
    return results
