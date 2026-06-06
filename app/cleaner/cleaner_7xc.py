# -*- coding: utf-8 -*-
"""七星彩 清洗器

TXT 格式（data.17500.cn 实际格式）：
期号 日期 位1 位2 位3 位4 位5 位6 位7 销售额 奖池 [更多奖金数据...]
例: 04101 2004-05-21 8 5 5 8 5 1 1 14725016 38860000 ...

每位号码 0-9，可重复。不含特别号。
"""

from app.cleaner.base_cleaner import BaseCleaner


class QxcCleaner(BaseCleaner):
    @property
    def fields(self) -> list[str]:
        return [
            "draw_num", "draw_date",
            "num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "num_7",
            "sales_amount", "prize_pool",
        ]

    def parse_line(self, line: str) -> dict:
        parts = line.split()
        if len(parts) < 10:
            return None

        draw_num = parts[0].strip()
        draw_date = parts[1].strip()
        nums = [int(p) for p in parts[2:9]]

        # 销量和奖池（parts[9]=销售额, parts[10]=奖池）
        sales = None
        prize = None
        if len(parts) >= 10:
            try:
                sales = float(parts[9])
            except ValueError:
                pass
        if len(parts) >= 11:
            try:
                prize = float(parts[10])
            except ValueError:
                pass

        if not draw_num.isdigit():
            return None
        # 七星彩每位 0-9
        if any(n < 0 or n > 9 for n in nums):
            return None

        return {
            "draw_num": draw_num,
            "draw_date": draw_date,
            "num_1": nums[0], "num_2": nums[1], "num_3": nums[2],
            "num_4": nums[3], "num_5": nums[4], "num_6": nums[5],
            "num_7": nums[6],
            "sales_amount": sales,
            "prize_pool": prize,
        }
