# -*- coding: utf-8 -*-
"""双色球 爬虫"""

from app.core.config import DATA_SOURCES
from app.crawler.base_crawler import BaseCrawler


class SsqCrawler(BaseCrawler):
    @property
    def url(self) -> str:
        return DATA_SOURCES["lottery_ssq"]["url"]

    @property
    def encoding(self) -> str:
        return DATA_SOURCES["lottery_ssq"]["encoding"]
