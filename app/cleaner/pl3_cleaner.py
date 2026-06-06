# -*- coding: utf-8 -*-
"""排列3 清洗器

TXT 格式假设（按实际数据源调整）：
期号 日期 百位 十位 个位
例: 2026001 2026-01-01 3 7 2
"""

from app.cleaner.base_cleaner import BaseCleaner


class Pl3Cleaner(BaseCleaner):
    @property
    def fields(self) -> list[str]:
        return ["draw_num", "draw_date", "num_1", "num_2", "num_3"]

    def parse_line(self, line: str) -> dict:
        parts = line.split()
        if len(parts) < 5:
            return None

        draw_num = parts[0].strip()
        draw_date = parts[1].strip()
        nums = [int(p) for p in parts[2:5]]

        # 校验
        if not draw_num.isdigit():
            return None
        if any(n < 0 or n > 9 for n in nums):
            return None

        return {
            "draw_num": draw_num,
            "draw_date": draw_date,
            "num_1": nums[0],
            "num_2": nums[1],
            "num_3": nums[2],
        }
