# -*- coding: utf-8 -*-
"""双色球 扩展统计 - numpy 加速版

双色球 = 红球6个(1-33) + 蓝球1个(1-16)
参考大乐透模式：area / sum_span / odd_even_size / zone / hot_cold / ratio
"""

import logging
import numpy as np
from app.core.database import db

logger = logging.getLogger(__name__)

RED_FIELDS = ["red_1", "red_2", "red_3", "red_4", "red_5", "red_6"]
BLUE_FIELDS = ["blue_1"]
ALL_FIELDS = RED_FIELDS + BLUE_FIELDS
ZONES = [
    ("zone_1", 1, 11),
    ("zone_2", 12, 22),
    ("zone_3", 23, 33),
]
BIG_THRESHOLD = 17


def _get_records(date=None, end_date=None):
    return db.fetch_all("lottery_ssq", date=date, end_date=end_date)


def _records_to_array(records, fields):
    data = []
    for r in records:
        row = []
        for f in fields:
            v = r.get(f)
            row.append(v if v is not None else np.nan)
        data.append(row)
    return np.array(data, dtype=float)


def area_stats(date=None, end_date=None) -> dict:
    """红球+蓝球区域频率"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, ALL_FIELDS)

    # 红球频率
    red_arr = arr[:, :6]
    red_valid = red_arr[~np.isnan(red_arr)]
    r_vals, r_counts = np.unique(red_valid, return_counts=True)
    red_freq = {str(int(v)): int(c) for v, c in zip(r_vals, r_counts) if not np.isnan(v)}

    # 蓝球频率
    blue_arr = arr[:, 6]
    blue_valid = blue_arr[~np.isnan(blue_arr)]
    b_vals, b_counts = np.unique(blue_valid, return_counts=True)
    blue_freq = {str(int(v)): int(c) for v, c in zip(b_vals, b_counts) if not np.isnan(v)}

    return {
        "red_area": dict(sorted(red_freq.items(), key=lambda x: int(x[0]))),
        "blue_area": dict(sorted(blue_freq.items(), key=lambda x: int(x[0]))),
    }


def sum_span_stats(date=None, end_date=None) -> dict:
    """红球和值+跨度统计"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, RED_FIELDS)
    valid_rows = ~np.isnan(arr).any(axis=1)
    reds = arr[valid_rows]

    if reds.size == 0:
        return {
            "sum_avg": 0, "sum_min": 0, "sum_max": 0, "sum_std": 0,
            "sum_p25": 0, "sum_p50": 0, "sum_p75": 0,
            "span_avg": 0, "span_min": 0, "span_max": 0, "span_std": 0,
        }

    sums = np.sum(reds, axis=1)
    spans = np.max(reds, axis=1) - np.min(reds, axis=1)

    return {
        "sum_avg": round(float(np.mean(sums)), 1),
        "sum_min": int(np.min(sums)),
        "sum_max": int(np.max(sums)),
        "sum_std": round(float(np.std(sums, ddof=1)), 2),
        "sum_p25": int(np.percentile(sums, 25)),
        "sum_p50": int(np.percentile(sums, 50)),
        "sum_p75": int(np.percentile(sums, 75)),
        "span_avg": round(float(np.mean(spans)), 1),
        "span_min": int(np.min(spans)),
        "span_max": int(np.max(spans)),
        "span_std": round(float(np.std(spans, ddof=1)), 2),
    }


def odd_even_size_stats(date=None, end_date=None) -> dict:
    """红球奇偶/大小汇总"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, RED_FIELDS)
    valid = arr[~np.isnan(arr)]

    odd = int(np.sum(valid % 2 == 1))
    even = int(np.sum(valid % 2 == 0))
    big = int(np.sum(valid >= BIG_THRESHOLD))
    small = int(np.sum(valid < BIG_THRESHOLD))
    total = odd + even

    return {
        "odd_count": odd, "even_count": even,
        "odd_ratio": f"{odd / total * 100:.1f}%" if total else "0%",
        "even_ratio": f"{even / total * 100:.1f}%" if total else "0%",
        "big_count": big, "small_count": small,
        "big_ratio": f"{big / total * 100:.1f}%" if total else "0%",
        "small_ratio": f"{small / total * 100:.1f}%" if total else "0%",
    }


def zone_stats(date=None, end_date=None) -> dict:
    """红球三区分布"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, RED_FIELDS)
    valid = arr[~np.isnan(arr)]

    edges = [1, 12, 23, 34]
    counts, _ = np.histogram(valid, bins=edges)

    result = {}
    for i, (name, low, high) in enumerate(ZONES):
        result[name] = {"range": f"{low}-{high}", "count": int(counts[i])}
    return result


def hot_cold_stats(date=None, end_date=None) -> dict:
    """红球冷热号Top10（近30期）"""
    records = _get_records(date, end_date)
    if not records:
        return {"hot": [], "cold": []}

    recent = records[:30]
    arr = _records_to_array(recent, RED_FIELDS)
    valid = arr[~np.isnan(arr)].astype(int)

    values, counts = np.unique(valid, return_counts=True)
    sorted_idx = np.argsort(-counts)

    hot = [{"number": int(values[i]), "count": int(counts[i])} for i in sorted_idx[:10]]

    appeared = set(values)
    all_nums = set(range(1, 34))
    cold_nums = sorted(all_nums - appeared)[:10]
    cold = [{"number": n, "count": 0} for n in cold_nums]

    if len(cold) < 10:
        for i in sorted_idx[::-1]:
            if len(cold) >= 10:
                break
            n = int(values[i])
            if n not in [x["number"] for x in cold]:
                cold.append({"number": n, "count": int(counts[i])})

    return {"hot": hot, "cold": cold}


def ratio_stats(date=None, end_date=None) -> dict:
    """红球奇偶比/大小比走势（近50期）"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, RED_FIELDS)
    result = []

    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != 6:
            continue
        nums = valid.astype(int)
        odd = int(np.sum(nums % 2 == 1))
        even = 6 - odd
        big = int(np.sum(nums >= BIG_THRESHOLD))
        small = 6 - big

        result.append({
            "draw_num": r.get("draw_num"),
            "odd_even_ratio": f"{odd}:{even}",
            "big_small_ratio": f"{big}:{small}",
        })

    return {"records": result}
