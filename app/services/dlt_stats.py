# -*- coding: utf-8 -*-
"""超级大乐透 扩展统计（4项）- numpy 加速版"""

import numpy as np
from app.core.database import db
from app.core.numpy_utils import records_to_array

FRONT_FIELDS = ["front_1", "front_2", "front_3", "front_4", "front_5"]
BACK_FIELDS = ["back_1", "back_2"]
ALL_FIELDS = FRONT_FIELDS + BACK_FIELDS
BIG_THRESHOLD = 18

POS_LABELS = ["前区1", "前区2", "前区3", "前区4", "前区5", "后区1", "后区2"]
FRONT_RANGE = list(range(1, 36))
BACK_RANGE = list(range(1, 13))


def _get_records(date=None, end_date=None):
    return db.fetch_all("lottery_dlt", date=date, end_date=end_date)


def _get_trend_records(date=None, end_date=None, limit=500):
    """走势图专用：限制返回条数，避免数据过载"""
    records = db.fetch_all("lottery_dlt", date=date, end_date=end_date)
    if not date and not end_date:
        return records[:limit]
    return records


# ========== 1. 热力图（位置×号码频率） ==========
def position_stats(date=None, end_date=None) -> dict:
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


# ========== 2. 冷热号 ==========
def hot_cold_stats(date=None, end_date=None) -> dict:
    records = _get_records(date, end_date)
    if not records:
        return {"hot": [], "cold": []}
    # 仅在无日期筛选时限制最近50期，有日期范围则用全量
    if not date and not end_date:
        records = records[:50]
    arr = records_to_array(records, FRONT_FIELDS)
    valid = arr[~np.isnan(arr)].astype(int)
    vals, cnts = np.unique(valid, return_counts=True)
    si = np.argsort(-cnts)
    hot = [{"number": int(vals[i]), "count": int(cnts[i])} for i in si[:10]]
    appeared = set(vals)
    cold_nums = sorted(set(range(1, 36)) - appeared)[:10]
    cold = [{"number": n, "count": 0} for n in cold_nums]
    if len(cold) < 10:
        for i in si[::-1]:
            if len(cold) >= 10: break
            n = int(vals[i])
            if n not in [x["number"] for x in cold]:
                cold.append({"number": n, "count": int(cnts[i])})
    return {"hot": hot, "cold": cold}


# ========== 3. 和值跨度走势 ==========
def period_list_stats(date=None, end_date=None) -> dict:
    records = _get_trend_records(date, end_date)
    arr = records_to_array(records, FRONT_FIELDS)
    period_list = []
    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != 5: continue
        nums = valid.astype(int)
        period_list.append({
            "draw_num": r.get("draw_num"),
            "sum_val": int(np.sum(nums)),
            "span": int(np.max(nums) - np.min(nums)),
        })
    return {"records": period_list}


# ========== 4. 奇偶比/大小比 ==========
def ratio_stats(date=None, end_date=None) -> dict:
    records = _get_trend_records(date, end_date)
    arr = records_to_array(records, FRONT_FIELDS)
    result = []
    for idx, r in enumerate(records):
        row = arr[idx]
        valid = row[~np.isnan(row)]
        if len(valid) != 5: continue
        nums = valid.astype(int)
        odd = int(np.sum(nums % 2 == 1))
        big = int(np.sum(nums >= BIG_THRESHOLD))
        result.append({
            "draw_num": r.get("draw_num"),
            "odd_even_ratio": f"{odd}:{5-odd}",
            "big_small_ratio": f"{big}:{5-big}",
        })
    return {"records": result}
