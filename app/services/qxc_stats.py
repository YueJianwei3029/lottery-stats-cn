# -*- coding: utf-8 -*-
"""七乐彩 扩展统计"""

import logging
from collections import Counter
from app.core.database import db

logger = logging.getLogger(__name__)

NUM_FIELDS = ["num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "num_7"]
BIG_THRESHOLD = 5   # 0-9, >=5 为大


def _get_records(date: str = None, end_date: str = None):
    return db.fetch_all("lottery_7xc", date=date, end_date=end_date)


def position_stats(date: str = None, end_date: str = None) -> dict:
    """各位置号码出现次数"""
    records = _get_records(date, end_date)
    result = {f"pos_{i + 1}": {} for i in range(7)}

    for r in records:
        for i, f in enumerate(NUM_FIELDS):
            v = r.get(f)
            if v:
                key = str(v)
                result[f"pos_{i + 1}"][key] = result[f"pos_{i + 1}"].get(key, 0) + 1

    # 排序
    for pos in result:
        result[pos] = dict(sorted(result[pos].items(), key=lambda x: int(x[0])))
    return result


def period_list_stats(date: str = None, end_date: str = None) -> dict:
    """全期奇偶/大小/和值/跨度列表"""
    records = _get_records(date, end_date)
    period_list = []

    for r in records:
        nums = [r.get(f) for f in NUM_FIELDS if r.get(f) is not None]
        if len(nums) != 7:
            continue

        odd = sum(1 for n in nums if n % 2 == 1)
        even = 7 - odd
        big = sum(1 for n in nums if n >= BIG_THRESHOLD)
        small = 7 - big

        period_list.append({
            "draw_num": r.get("draw_num"),
            "draw_date": str(r.get("draw_date", "")),
            "odd_count": odd,
            "even_count": even,
            "big_count": big,
            "small_count": small,
            "sum_val": sum(nums),
            "span": max(nums) - min(nums),
        })

    return {"records": period_list}


def digit_freq_stats(date: str = None, end_date: str = None) -> dict:
    """0-9 数字全位置出现频率统计（取个位数）"""
    records = _get_records(date, end_date)
    freq = {str(i): 0 for i in range(10)}

    for r in records:
        for f in NUM_FIELDS:
            v = r.get(f)
            if v is not None:
                digit = str(v % 10)
                freq[digit] += 1

    return {"digit_freq": freq}


def hot_cold_stats(date: str = None, end_date: str = None) -> dict:
    """近 10 期热号/冷号 Top5"""
    records = _get_records(date, end_date)
    if not records:
        return {"hot": [], "cold": []}

    # 取最近 10 期
    recent = records[:10]
    counter = Counter()
    for r in recent:
        for f in NUM_FIELDS:
            v = r.get(f)
            if v:
                counter[v] += 1

    # 热号 Top5（出现次数最多）
    hot = [{"number": n, "count": c} for n, c in counter.most_common(5)]

    # 冷号：1-30 中从未出现的号码，取 5 个
    all_nums = set(range(1, 31))
    appeared = set(counter.keys())
    cold_nums = sorted(all_nums - appeared)[:5]
    cold = [{"number": n, "count": 0} for n in cold_nums]

    # 如果冷号不够 5 个，用出现最少的补
    if len(cold) < 5:
        remaining = sorted(counter.items(), key=lambda x: x[1])
        for n, c in remaining:
            if len(cold) >= 5:
                break
            if n not in [x["number"] for x in cold]:
                cold.append({"number": n, "count": c})

    return {"hot": hot, "cold": cold}


def ratio_stats(date: str = None, end_date: str = None) -> dict:
    """单期奇偶比、大小比、012路分布"""
    records = _get_records(date, end_date)
    result = []

    for r in records:
        nums = [r.get(f) for f in NUM_FIELDS if r.get(f) is not None]
        if len(nums) != 7:
            continue

        odd = sum(1 for n in nums if n % 2 == 1)
        even = 7 - odd
        big = sum(1 for n in nums if n >= BIG_THRESHOLD)
        small = 7 - big

        # 012 路
        road = {"0": 0, "1": 0, "2": 0}
        for n in nums:
            road[str(n % 3)] += 1

        result.append({
            "draw_num": r.get("draw_num"),
            "odd_even_ratio": f"{odd}:{even}",
            "big_small_ratio": f"{big}:{small}",
            "road_012": road,
        })

    return {"records": result}


def trend_stats(date: str = None, end_date: str = None) -> dict:
    """销量/奖池趋势（预留）"""
    records = _get_records(date, end_date)
    result = []
    for r in records:
        result.append({
            "draw_num": r.get("draw_num"),
            "draw_date": str(r.get("draw_date", "")),
            "sales_amount": r.get("sales_amount"),
            "prize_pool": r.get("prize_pool"),
        })
    return {"records": result}
