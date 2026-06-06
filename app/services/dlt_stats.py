# -*- coding: utf-8 -*-
"""超级大乐透 扩展统计"""

import logging
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


def _get_records(date: str = None, end_date: str = None):
    return db.fetch_all("lottery_dlt", date=date, end_date=end_date)


def area_stats(date: str = None, end_date: str = None) -> dict:
    """前区/后区分区号码出现次数"""
    records = _get_records(date, end_date)
    front_freq = {}
    back_freq = {}

    for r in records:
        for f in FRONT_FIELDS:
            v = r.get(f)
            if v:
                front_freq[str(v)] = front_freq.get(str(v), 0) + 1
        for f in BACK_FIELDS:
            v = r.get(f)
            if v:
                back_freq[str(v)] = back_freq.get(str(v), 0) + 1

    return {
        "front_area": dict(sorted(front_freq.items(), key=lambda x: int(x[0]))),
        "back_area": dict(sorted(back_freq.items(), key=lambda x: int(x[0]))),
    }


def sum_span_stats(date: str = None, end_date: str = None) -> dict:
    """前区和值 + 跨度统计（全期汇总）"""
    records = _get_records(date, end_date)
    sums = []
    spans = []

    for r in records:
        fronts = [r.get(f) for f in FRONT_FIELDS if r.get(f) is not None]
        if len(fronts) == 5:
            sums.append(sum(fronts))
            spans.append(max(fronts) - min(fronts))

    if not sums:
        return {"sum_avg": 0, "sum_min": 0, "sum_max": 0, "span_avg": 0, "span_min": 0, "span_max": 0}

    return {
        "sum_avg": round(sum(sums) / len(sums), 1),
        "sum_min": min(sums),
        "sum_max": max(sums),
        "span_avg": round(sum(spans) / len(spans), 1),
        "span_min": min(spans),
        "span_max": max(spans),
    }


def odd_even_size_stats(date: str = None, end_date: str = None) -> dict:
    """前区号码奇偶、大小专项汇总"""
    records = _get_records(date, end_date)
    odd = 0
    even = 0
    big = 0
    small = 0

    for r in records:
        for f in FRONT_FIELDS:
            v = r.get(f)
            if v is None:
                continue
            if v % 2 == 1:
                odd += 1
            else:
                even += 1
            if v >= 18:
                big += 1
            else:
                small += 1

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
    zone_count = {name: 0 for name, _, _ in ZONES}

    for r in records:
        for f in FRONT_FIELDS:
            v = r.get(f)
            if v is None:
                continue
            for name, low, high in ZONES:
                if low <= v <= high:
                    zone_count[name] += 1
                    break

    result = {}
    for name, low, high in ZONES:
        result[name] = {"range": f"{low}-{high}", "count": zone_count[name]}
    return result
