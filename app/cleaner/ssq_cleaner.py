# -*- coding: utf-8 -*-
"""双色球 清洗器

TXT 格式假设（按实际数据源调整）：
期号 日期 红1 红2 红3 红4 红5 红6 蓝
例: 2026001 2026-01-01 1 5 12 18 25 33 8
"""

from app.cleaner.base_cleaner import BaseCleaner


class SsqCleaner(BaseCleaner):
    @property
    def fields(self) -> list[str]:
        return [
            "draw_num", "draw_date",
            "red_1", "red_2", "red_3", "red_4", "red_5", "red_6",
            "blue_1",
        ]

    def parse_line(self, line: str) -> dict:
        parts = line.split()
        if len(parts) < 9:
            return None

        draw_num = parts[0].strip()
        draw_date = parts[1].strip()
        reds = [int(p) for p in parts[2:8]]
        blue = int(parts[8])

        if not draw_num.isdigit():
            return None
        if any(n < 1 or n > 33 for n in reds):
            return None
        if blue < 1 or blue > 16:
            return None

        return {
            "draw_num": draw_num,
            "draw_date": draw_date,
            "red_1": reds[0], "red_2": reds[1], "red_3": reds[2],
            "red_4": reds[3], "red_5": reds[4], "red_6": reds[5],
            "blue_1": blue,
        }
