# -*- coding: utf-8 -*-
"""排列5 爬虫"""

from app.core.config import DATA_SOURCES
from app.crawler.base_crawler import BaseCrawler


class Pl5Crawler(BaseCrawler):
    @property
    def url(self) -> str:
        return DATA_SOURCES["lottery_pl5"]["url"]

    @property
    def encoding(self) -> str:
        return DATA_SOURCES["lottery_pl5"]["encoding"]
