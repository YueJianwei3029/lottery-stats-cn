# -*- coding: utf-8 -*-
"""七乐彩 爬虫"""

from app.core.config import DATA_SOURCES
from app.crawler.base_crawler import BaseCrawler


class QxcCrawler(BaseCrawler):
    @property
    def url(self) -> str:
        return DATA_SOURCES["lottery_7xc"]["url"]

    @property
    def encoding(self) -> str:
        return DATA_SOURCES["lottery_7xc"]["encoding"]
