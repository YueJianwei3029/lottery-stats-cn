# -*- coding: utf-8 -*-
"""超级大乐透 清洗器

TXT 格式假设（按实际数据源调整）：
期号 日期 前1 前2 前3 前4 前5 后1 后2
例: 2026001 2026-01-01 5 12 18 25 33 3 8
"""

from app.cleaner.base_cleaner import BaseCleaner


class DltCleaner(BaseCleaner):
    @property
    def fields(self) -> list[str]:
        return [
            "draw_num", "draw_date",
            "front_1", "front_2", "front_3", "front_4", "front_5",
            "back_1", "back_2",
        ]

    def parse_line(self, line: str) -> dict:
        parts = line.split()
        if len(parts) < 9:
            return None

        draw_num = parts[0].strip()
        draw_date = parts[1].strip()
        fronts = [int(p) for p in parts[2:7]]
        backs = [int(p) for p in parts[7:9]]

        if not draw_num.isdigit():
            return None
        if any(n < 1 or n > 35 for n in fronts):
            return None
        if any(n < 1 or n > 12 for n in backs):
            return None

        return {
            "draw_num": draw_num,
            "draw_date": draw_date,
            "front_1": fronts[0], "front_2": fronts[1], "front_3": fronts[2],
            "front_4": fronts[3], "front_5": fronts[4],
            "back_1": backs[0], "back_2": backs[1],
        }
