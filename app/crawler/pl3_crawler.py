# -*- coding: utf-8 -*-
"""排列3 爬虫"""

from app.core.config import DATA_SOURCES
from app.crawler.base_crawler import BaseCrawler


class Pl3Crawler(BaseCrawler):
    @property
    def url(self) -> str:
        return DATA_SOURCES["lottery_pl3"]["url"]

    @property
    def encoding(self) -> str:
        return DATA_SOURCES["lottery_pl3"]["encoding"]
