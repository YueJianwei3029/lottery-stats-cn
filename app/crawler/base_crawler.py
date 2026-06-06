# -*- coding: utf-8 -*-
"""爬虫基类"""

import logging
import requests
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """爬虫基类：子类只需覆写 url 和 encoding"""

    @property
    @abstractmethod
    def url(self) -> str:
        """数据源 URL"""
        ...

    @property
    def encoding(self) -> str:
        """文本编码"""
        return "utf-8"

    @property
    def timeout(self) -> int:
        """请求超时（秒）"""
        return 30

    @property
    def headers(self) -> dict:
        """请求头"""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

    def fetch(self) -> str:
        """
        下载 TXT 文本数据
        :return: 原始文本内容
        """
        try:
            logger.info(f"[Crawler] 开始下载: {self.url}")
            resp = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            resp.encoding = self.encoding
            logger.info(f"[Crawler] 下载完成: {len(resp.text)} 字符")
            return resp.text
        except requests.RequestException as e:
            logger.error(f"[Crawler] 下载失败: {e}")
            return ""
