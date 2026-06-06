# -*- coding: utf-8 -*-
"""七星彩 扩展统计 - numpy 加速版"""

import logging
import numpy as np
from app.core.database import db

logger = logging.getLogger(__name__)

NUM_FIELDS = ["num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "num_7"]
BIG_THRESHOLD = 5


def _get_records(date: str = None, end_date: str = None):
    return db.fetch_all("lottery_7xc", date=date, end_date=end_date)


def _records_to_array(records, fields):
    data = []
    for r in records:
        row = []
        for f in fields:
            v = r.get(f)
            row.append(v if v is not None else np.nan)
        data.append(row)
    return np.array(data, dtype=float)


def position_stats(date: str = None, end_date: str = None) -> dict:
    """各位置号码出现次数"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, NUM_FIELDS)
    result = {}

    for i in range(7):
        col = arr[:, i]
        valid = col[~np.isnan(col)]
        values, counts = np.unique(valid, return_counts=True)
        freq = {str(int(v)): int(c) for v, c in zip(values, counts) if not np.isnan(v)}
        result[f"pos_{i + 1}"] = dict(sorted(freq.items(), key=lambda x: int(x[0])))

    return result


def period_list_stats(date: str = None, end_date: str = None) -> dict:
    """全期奇偶/大小/和值/跨度列表"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, NUM_FIELDS)
    period_list = []

    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != 7:
            continue

        nums = valid.astype(int)
        odd = int(np.sum(nums % 2 == 1))
        even = 7 - odd
        big = int(np.sum(nums >= BIG_THRESHOLD))
        small = 7 - big

        period_list.append({
            "draw_num": r.get("draw_num"),
            "draw_date": str(r.get("draw_date", "")),
            "odd_count": odd,
            "even_count": even,
            "big_count": big,
            "small_count": small,
            "sum_val": int(np.sum(nums)),
            "span": int(np.max(nums) - np.min(nums)),
        })

    return {"records": period_list}


def digit_freq_stats(date: str = None, end_date: str = None) -> dict:
    """0-9 数字全位置出现频率统计（取个位数）"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, NUM_FIELDS)
    valid = arr[~np.isnan(arr)].astype(int)

    digits = valid % 10
    counts = np.bincount(digits, minlength=10)
    freq = {str(i): int(counts[i]) for i in range(10)}

    return {"digit_freq": freq}


def hot_cold_stats(date: str = None, end_date: str = None) -> dict:
    """近 10 期热号/冷号 Top5"""
    records = _get_records(date, end_date)
    if not records:
        return {"hot": [], "cold": []}

    recent = records[:10]
    arr = _records_to_array(recent, NUM_FIELDS)
    valid = arr[~np.isnan(arr)].astype(int)

    values, counts = np.unique(valid, return_counts=True)
    sorted_idx = np.argsort(-counts)

    # 热号 Top5
    hot = [{"number": int(values[i]), "count": int(counts[i])} for i in sorted_idx[:5]]

    # 冷号
    appeared = set(values)
    all_nums = set(range(10))
    cold_nums = sorted(all_nums - appeared)[:5]
    cold = [{"number": n, "count": 0} for n in cold_nums]

    if len(cold) < 5:
        for i in sorted_idx[::-1]:
            if len(cold) >= 5:
                break
            n = int(values[i])
            if n not in [x["number"] for x in cold]:
                cold.append({"number": n, "count": int(counts[i])})

    return {"hot": hot, "cold": cold}


def ratio_stats(date: str = None, end_date: str = None) -> dict:
    """单期奇偶比、大小比、012路分布"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, NUM_FIELDS)
    result = []

    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != 7:
            continue

        nums = valid.astype(int)
        odd = int(np.sum(nums % 2 == 1))
        even = 7 - odd
        big = int(np.sum(nums >= BIG_THRESHOLD))
        small = 7 - big

        road_vals = nums % 3
        road_counts = np.bincount(road_vals, minlength=3)
        road = {"0": int(road_counts[0]), "1": int(road_counts[1]), "2": int(road_counts[2])}

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
