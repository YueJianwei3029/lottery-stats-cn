# -*- coding: utf-8 -*-
"""七星彩 清洗器（2020年新规则：前区6位0-9 + 后区1位0-14）

TXT 格式（data.17500.cn 实际格式）：
期号 日期 前区1 前区2 前区3 前区4 前区5 前区6 后区 销售额 奖池 [更多奖金数据...]
例: 25001 2025-01-03 5 2 8 1 4 7 11 14725016 38860000 ...

新规则（2020年后）：前区6位0-9可重复，后区1位0-14。
"""

from app.cleaner.base_cleaner import BaseCleaner


class QxcCleaner(BaseCleaner):
    @property
    def fields(self) -> list[str]:
        return [
            "draw_num", "draw_date",
            "num_1", "num_2", "num_3", "num_4", "num_5", "num_6",
            "back_1",
            "sales_amount", "prize_pool",
        ]

    def parse_line(self, line: str) -> dict:
        parts = line.split()
        if len(parts) < 10:
            return None

        draw_num = parts[0].strip()
        draw_date = parts[1].strip()

        # 前区6位（parts[2:8]）0-9，后区1位（parts[8]）0-14
        front_nums = [int(p) for p in parts[2:8]]
        back_num = int(parts[8])

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
        # 前区校验：0-9
        if any(n < 0 or n > 9 for n in front_nums):
            return None
        # 后区校验：0-14
        if back_num < 0 or back_num > 14:
            return None

        return {
            "draw_num": draw_num,
            "draw_date": draw_date,
            "num_1": front_nums[0], "num_2": front_nums[1], "num_3": front_nums[2],
            "num_4": front_nums[3], "num_5": front_nums[4], "num_6": front_nums[5],
            "back_1": back_num,
            "sales_amount": sales,
            "prize_pool": prize,
        }
