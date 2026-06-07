# -*- coding: utf-8 -*-
"""七星彩 扩展统计（2020年新规则：前区6位0-9 + 后区1位0-14）- numpy 加速版"""

import logging
import numpy as np
from app.core.database import db
from app.core.numpy_utils import records_to_array

logger = logging.getLogger(__name__)

FRONT_FIELDS = ["num_1", "num_2", "num_3", "num_4", "num_5", "num_6"]
BACK_FIELD = "back_1"
ALL_FIELDS = FRONT_FIELDS + [BACK_FIELD]  # 共7个

FRONT_BIG_THRESHOLD = 5   # 前区0-9：≥5为大
BACK_BIG_THRESHOLD = 8    # 后区0-14：≥8为大

POS_LABELS = ["前区1", "前区2", "前区3", "前区4", "前区5", "前区6", "后区"]


def _get_records(date=None, end_date=None):
    return db.fetch_all("lottery_7xc", date=date, end_date=end_date)


def _get_trend_records(date=None, end_date=None, limit=500):
    """走势图专用：限制返回条数，避免数据过载"""
    records = db.fetch_all("lottery_7xc", date=date, end_date=end_date)
    if not date and not end_date:
        return records[:limit]
    return records


# ========== 1. 热力图（位置×号码频率） ==========
def position_stats(date=None, end_date=None) -> dict:
    """各位置号码出现次数（前区6位0-9 + 后区0-14）"""
    records = _get_records(date, end_date)
    arr = records_to_array(records, ALL_FIELDS)
    result = {}
    for i in range(7):
        col = arr[:, i]
        valid = col[~np.isnan(col)]
        vals, cnts = np.unique(valid, return_counts=True)
        freq = {str(int(v)): int(c) for v, c in zip(vals, cnts) if not np.isnan(v)}
        result[f"pos_{i+1}"] = dict(sorted(freq.items(), key=lambda x: int(x[0])))
    return result


# ========== 2. 冷热号（前区0-9 和后区0-14 分开统计） ==========
def _hot_cold_for_zone(records, zone_fields, num_range):
    """通用冷热号计算：对指定字段和号码范围统计"""
    if not records:
        return [], []
    arr = records_to_array(records, zone_fields)
    valid = arr[~np.isnan(arr)].astype(int)
    vals, cnts = np.unique(valid, return_counts=True)
    si = np.argsort(-cnts)

    hot = [{"number": int(vals[i]), "count": int(cnts[i])} for i in si[:5]]

    appeared = set(vals)
    all_nums = set(range(num_range[0], num_range[1] + 1))
    cold_nums = sorted(all_nums - appeared)[:5]
    cold = [{"number": n, "count": 0} for n in cold_nums]
    if len(cold) < 5:
        for i in si[::-1]:
            if len(cold) >= 5:
                break
            n = int(vals[i])
            if n not in [x["number"] for x in cold]:
                cold.append({"number": n, "count": int(cnts[i])})

    return hot, cold


def hot_cold_stats(date=None, end_date=None) -> dict:
    """近 50 期热号/冷号（前区0-9 和后区0-14 分开统计）"""
    records = _get_records(date, end_date)
    if not records:
        return {"hot": [], "cold": []}
    if not date and not end_date:
        records = records[:50]

    front_hot, front_cold = _hot_cold_for_zone(records, FRONT_FIELDS, (0, 9))
    back_hot, back_cold = _hot_cold_for_zone(records, [BACK_FIELD], (0, 14))

    return {
        "front": {"hot": front_hot, "cold": front_cold},
        "back": {"hot": back_hot, "cold": back_cold},
    }


# ========== 3. 和值跨度走势（前区+后区分开统计） ==========
def period_list_stats(date=None, end_date=None) -> dict:
    """全期走势：前区和值/跨度 + 后区值"""
    records = _get_trend_records(date, end_date)
    arr = records_to_array(records, ALL_FIELDS)
    period_list = []

    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != 7:
            continue

        nums = valid.astype(int)
        front = nums[:6]
        back = nums[6]

        period_list.append({
            "draw_num": r.get("draw_num"),
            "draw_date": str(r.get("draw_date", "")),
            "front_sum": int(np.sum(front)),
            "front_span": int(np.max(front) - np.min(front)),
            "back_val": int(back),
            "total_sum": int(np.sum(nums)),
        })

    return {"records": period_list}


# ========== 4. 奇偶比/大小比（前区后区分开） ==========
def ratio_stats(date=None, end_date=None) -> dict:
    """单期奇偶比、大小比（前区6位 + 后区1位分开）"""
    records = _get_trend_records(date, end_date)
    arr = records_to_array(records, ALL_FIELDS)
    result = []

    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != 7:
            continue

        nums = valid.astype(int)
        front = nums[:6]
        back = nums[6]

        # 前区统计
        f_odd = int(np.sum(front % 2 == 1))
        f_big = int(np.sum(front >= FRONT_BIG_THRESHOLD))
        # 后区统计
        b_odd = 1 if back % 2 == 1 else 0
        b_big = 1 if back >= BACK_BIG_THRESHOLD else 0

        result.append({
            "draw_num": r.get("draw_num"),
            "front_odd_even": f"{f_odd}:{6 - f_odd}",
            "front_big_small": f"{f_big}:{6 - f_big}",
            "back_odd_even": f"{b_odd}:{1 - b_odd}",
            "back_big_small": f"{b_big}:{1 - b_big}",
        })

    return {"records": result}


# ========== 5. 数字频率（前区0-9，取个位数） ==========
def digit_freq_stats(date=None, end_date=None) -> dict:
    """前区0-9数字出现频率统计（取个位数，仅前区）"""
    records = _get_records(date, end_date)
    arr = records_to_array(records, FRONT_FIELDS)
    valid = arr[~np.isnan(arr)].astype(int)

    digits = valid % 10
    counts = np.bincount(digits, minlength=10)
    freq = {str(i): int(counts[i]) for i in range(10)}

    return {"digit_freq": freq}


# ========== 6. 销量/奖池趋势 ==========
def trend_stats(date=None, end_date=None) -> dict:
    """销量/奖池趋势"""
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
