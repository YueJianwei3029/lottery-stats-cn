# -*- coding: utf-8 -*-
"""超级大乐透 爬虫"""

from app.core.config import DATA_SOURCES
from app.crawler.base_crawler import BaseCrawler


class DltCrawler(BaseCrawler):
    @property
    def url(self) -> str:
        return DATA_SOURCES["lottery_dlt"]["url"]

    @property
    def encoding(self) -> str:
        return DATA_SOURCES["lottery_dlt"]["encoding"]
