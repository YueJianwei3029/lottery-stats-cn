# -*- coding: utf-8 -*-
"""超级大乐透 扩展统计 - numpy 加速版"""

import logging
import numpy as np
from app.core.database import db

logger = logging.getLogger(__name__)

FRONT_FIELDS = ["front_1", "front_2", "front_3", "front_4", "front_5"]
BACK_FIELDS = ["back_1", "back_2"]
ZONES = [
    ("zone_1", 1, 7),
    ("zone_2", 8, 14),
    ("zone_3", 15, 21),
    ("zone_4", 22, 28),
    ("zone_5", 29, 35),
]
BIG_THRESHOLD = 18


def _get_records(date: str = None, end_date: str = None):
    return db.fetch_all("lottery_dlt", date=date, end_date=end_date)


def _records_to_array(records, fields):
    """将记录列表转换为 numpy 二维数组"""
    data = []
    for r in records:
        row = []
        for f in fields:
            v = r.get(f)
            row.append(v if v is not None else np.nan)
        data.append(row)
    return np.array(data, dtype=float)


def area_stats(date: str = None, end_date: str = None) -> dict:
    """前区/后区分区号码出现次数"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, FRONT_FIELDS + BACK_FIELDS)

    # 前区频率
    front_arr = arr[:, :5]
    front_valid = front_arr[~np.isnan(front_arr)]
    front_values, front_counts = np.unique(front_valid, return_counts=True)
    front_freq = {str(int(v)): int(c) for v, c in zip(front_values, front_counts) if not np.isnan(v)}

    # 后区频率
    back_arr = arr[:, 5:7]
    back_valid = back_arr[~np.isnan(back_arr)]
    back_values, back_counts = np.unique(back_valid, return_counts=True)
    back_freq = {str(int(v)): int(c) for v, c in zip(back_values, back_counts) if not np.isnan(v)}

    return {
        "front_area": dict(sorted(front_freq.items(), key=lambda x: int(x[0]))),
        "back_area": dict(sorted(back_freq.items(), key=lambda x: int(x[0]))),
    }


def sum_span_stats(date: str = None, end_date: str = None) -> dict:
    """前区和值 + 跨度统计（全期汇总）- 含分位数与标准差"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, FRONT_FIELDS)
    valid_rows = ~np.isnan(arr).any(axis=1)
    fronts_arr = arr[valid_rows]

    if fronts_arr.size == 0:
        return {
            "sum_avg": 0, "sum_min": 0, "sum_max": 0, "sum_std": 0,
            "sum_p25": 0, "sum_p50": 0, "sum_p75": 0,
            "span_avg": 0, "span_min": 0, "span_max": 0, "span_std": 0,
        }

    sums = np.sum(fronts_arr, axis=1)
    spans = np.max(fronts_arr, axis=1) - np.min(fronts_arr, axis=1)

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


def odd_even_size_stats(date: str = None, end_date: str = None) -> dict:
    """前区号码奇偶、大小专项汇总"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, FRONT_FIELDS)
    valid = arr[~np.isnan(arr)]

    odd = int(np.sum(valid % 2 == 1))
    even = int(np.sum(valid % 2 == 0))
    big = int(np.sum(valid >= BIG_THRESHOLD))
    small = int(np.sum(valid < BIG_THRESHOLD))
    total = odd + even

    return {
        "odd_count": odd,
        "even_count": even,
        "odd_ratio": f"{odd / total * 100:.1f}%" if total else "0%",
        "even_ratio": f"{even / total * 100:.1f}%" if total else "0%",
        "big_count": big,
        "small_count": small,
        "big_ratio": f"{big / total * 100:.1f}%" if total else "0%",
        "small_ratio": f"{small / total * 100:.1f}%" if total else "0%",
    }


def zone_stats(date: str = None, end_date: str = None) -> dict:
    """前区 5 区间分布统计"""
    records = _get_records(date, end_date)
    arr = _records_to_array(records, FRONT_FIELDS)
    valid = arr[~np.isnan(arr)]

    zone_edges = [1, 8, 15, 22, 29, 36]
    counts, _ = np.histogram(valid, bins=zone_edges)

    result = {}
    for i, (name, low, high) in enumerate(ZONES):
        result[name] = {"range": f"{low}-{high}", "count": int(counts[i])}
    return result
