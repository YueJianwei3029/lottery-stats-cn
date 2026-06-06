# -*- coding: utf-8 -*-
"""清洗基类"""

import re
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseCleaner(ABC):
    """清洗基类：子类需覆写 fields 和 parse_line"""

    @property
    @abstractmethod
    def fields(self) -> list[str]:
        """数据字段列表（对应数据库表字段，不含自增 id）"""
        ...

    def parse(self, raw_text: str) -> list[dict]:
        """
        解析 TXT 文本为结构化数据列表

        :param raw_text: 原始文本
        :return: list[dict]，每条记录以 fields 为 key
        """
        if not raw_text:
            return []

        lines = raw_text.strip().split("\n")
        records = []
        skipped = 0

        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            try:
                record = self.parse_line(line)
                if record:
                    records.append(record)
                else:
                    skipped += 1
            except Exception as e:
                logger.warning(f"[Cleaner] 第 {line_no} 行解析失败: {e}")
                skipped += 1

        logger.info(f"[Cleaner] 解析完成: {len(records)} 条, 跳过 {skipped} 行")
        return records

    @abstractmethod
    def parse_line(self, line: str) -> dict:
        """
        解析单行 → dict

        :param line: 单行文本
        :return: dict 或 None（校验失败跳过）
        """
        ...
