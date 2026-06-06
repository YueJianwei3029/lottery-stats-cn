# -*- coding: utf-8 -*-
"""排列3/排列5 共用扩展统计 - numpy 加速版

PL3: num_1~3 (0-9) | PL5: num_1~5 (0-9)
参考七星彩模式：position / digit_freq / hot_cold / ratio / period_list
PL3 特有：type_analysis（组三/组六/豹子）
"""

import logging
import numpy as np
from app.core.database import db

logger = logging.getLogger(__name__)

PL3_FIELDS = ["num_1", "num_2", "num_3"]
PL5_FIELDS = ["num_1", "num_2", "num_3", "num_4", "num_5"]
BIG_THRESHOLD = 5


def _get_fields(n: int) -> list:
    return PL3_FIELDS if n == 3 else PL5_FIELDS


def _get_table(n: int) -> str:
    return "lottery_pl3" if n == 3 else "lottery_pl5"


def _records_to_array(records, fields):
    data = []
    for r in records:
        row = []
        for f in fields:
            v = r.get(f)
            row.append(v if v is not None else np.nan)
        data.append(row)
    return np.array(data, dtype=float)


def position_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    """各位置号码频率"""
    records = db.fetch_all(table, date=date, end_date=end_date)
    arr = _records_to_array(records, fields)
    n = len(fields)
    result = {}

    for i in range(n):
        col = arr[:, i]
        valid = col[~np.isnan(col)]
        values, counts = np.unique(valid, return_counts=True)
        freq = {str(int(v)): int(c) for v, c in zip(values, counts) if not np.isnan(v)}
        result[f"pos_{i + 1}"] = dict(sorted(freq.items(), key=lambda x: int(x[0])))

    return result


def digit_freq_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    """0-9 数字全位置频率"""
    records = db.fetch_all(table, date=date, end_date=end_date)
    arr = _records_to_array(records, fields)
    valid = arr[~np.isnan(arr)].astype(int)

    digits = valid % 10
    counts = np.bincount(digits, minlength=10)
    freq = {str(i): int(counts[i]) for i in range(10)}

    return {"digit_freq": freq}


def hot_cold_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    """近10期冷热号Top5"""
    records = db.fetch_all(table, date=date, end_date=end_date)
    if not records:
        return {"hot": [], "cold": []}

    recent = records[:10]
    arr = _records_to_array(recent, fields)
    valid = arr[~np.isnan(arr)].astype(int)

    values, counts = np.unique(valid, return_counts=True)
    sorted_idx = np.argsort(-counts)

    hot = [{"number": int(values[i]), "count": int(counts[i])} for i in sorted_idx[:5]]

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


def ratio_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    """奇偶比/大小比/012路分布"""
    records = db.fetch_all(table, date=date, end_date=end_date)
    arr = _records_to_array(records, fields)
    n = len(fields)
    result = []

    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != n:
            continue
        nums = valid.astype(int)
        odd = int(np.sum(nums % 2 == 1))
        even = n - odd
        big = int(np.sum(nums >= BIG_THRESHOLD))
        small = n - big

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


def period_list_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    """逐期和值+跨度+奇偶+大小"""
    records = db.fetch_all(table, date=date, end_date=end_date)
    arr = _records_to_array(records, fields)
    n = len(fields)
    period_list = []

    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != n:
            continue
        nums = valid.astype(int)
        odd = int(np.sum(nums % 2 == 1))
        even = n - odd
        big = int(np.sum(nums >= BIG_THRESHOLD))
        small = n - big

        period_list.append({
            "draw_num": r.get("draw_num"),
            "draw_date": str(r.get("draw_date", "")),
            "odd_count": odd, "even_count": even,
            "big_count": big, "small_count": small,
            "sum_val": int(np.sum(nums)),
            "span": int(np.max(nums) - np.min(nums)),
        })

    return {"records": period_list}


def type_analysis_stats(date=None, end_date=None) -> dict:
    """排列3专用：组三/组六/豹子统计"""
    records = db.fetch_all("lottery_pl3", date=date, end_date=end_date)
    arr = _records_to_array(records, PL3_FIELDS)
    type_3 = type_6 = type_baozi = 0

    for i in range(arr.shape[0]):
        row = arr[i]
        valid = row[~np.isnan(row)]
        if len(valid) != 3:
            continue
        nums = valid.astype(int)
        unique = len(set(nums.tolist()))
        if unique == 1:
            type_baozi += 1
        elif unique == 2:
            type_3 += 1
        else:
            type_6 += 1

    return {"type_3": type_3, "type_6": type_6, "type_baozi": type_baozi}
