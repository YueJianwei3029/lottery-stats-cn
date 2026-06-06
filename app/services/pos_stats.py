# -*- coding: utf-8 -*-
"""排列3/排列5 共用扩展统计（4项）- numpy 加速版"""

import logging
import numpy as np
from app.core.database import db

logger = logging.getLogger(__name__)

PL3_FIELDS = ["num_1", "num_2", "num_3"]
PL5_FIELDS = ["num_1", "num_2", "num_3", "num_4", "num_5"]
BIG_THRESHOLD = 5


def _get_trend_records(table, date=None, end_date=None, limit=500):
    """走势图专用：限制返回条数"""
    records = db.fetch_all(table, date=date, end_date=end_date)
    if not date and not end_date:
        return records[:limit]
    return records


def _records_to_array(records, fields):
    data = []
    for r in records:
        row = [r.get(f) if r.get(f) is not None else np.nan for f in fields]
        data.append(row)
    return np.array(data, dtype=float)


# ========== 1. 热力图 ==========
def position_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    records = db.fetch_all(table, date=date, end_date=end_date)
    arr = _records_to_array(records, fields)
    result = {}
    for i in range(len(fields)):
        col = arr[:, i]; valid = col[~np.isnan(col)]
        vals, cnts = np.unique(valid, return_counts=True)
        freq = {str(int(v)): int(c) for v, c in zip(vals, cnts) if not np.isnan(v)}
        result[f"pos_{i+1}"] = dict(sorted(freq.items(), key=lambda x: int(x[0])))
    return result


# ========== 2. 冷热号 ==========
def hot_cold_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    records = db.fetch_all(table, date=date, end_date=end_date)
    if not records: return {"hot": [], "cold": []}
    if not date and not end_date:
        records = records[:50]
    arr = _records_to_array(records, fields)
    valid = arr[~np.isnan(arr)].astype(int)
    vals, cnts = np.unique(valid, return_counts=True)
    si = np.argsort(-cnts)
    hot = [{"number": int(vals[i]), "count": int(cnts[i])} for i in si[:5]]
    appeared = set(vals)
    cold_nums = sorted(set(range(10)) - appeared)[:5]
    cold = [{"number": n, "count": 0} for n in cold_nums]
    if len(cold) < 5:
        for i in si[::-1]:
            if len(cold) >= 5: break
            n = int(vals[i])
            if n not in [x["number"] for x in cold]:
                cold.append({"number": n, "count": int(cnts[i])})
    return {"hot": hot, "cold": cold}


# ========== 3. 和值跨度走势 ==========
def period_list_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    records = _get_trend_records(table, date=date, end_date=end_date)
    arr = _records_to_array(records, fields)
    n = len(fields); period_list = []
    for idx, r in enumerate(records):
        row = arr[idx]; valid = row[~np.isnan(row)]
        if len(valid) != n: continue
        nums = valid.astype(int)
        period_list.append({
            "draw_num": r.get("draw_num"),
            "draw_date": str(r.get("draw_date", "")),
            "sum_val": int(np.sum(nums)),
            "span": int(np.max(nums) - np.min(nums)),
        })
    return {"records": period_list}


# ========== 4. 奇偶比/大小比 ==========
def ratio_stats(table: str, fields: list, date=None, end_date=None) -> dict:
    records = _get_trend_records(table, date=date, end_date=end_date)
    arr = _records_to_array(records, fields)
    n = len(fields); result = []
    for idx, r in enumerate(records):
        row = arr[idx]; valid = row[~np.isnan(row)]
        if len(valid) != n: continue
        nums = valid.astype(int)
        odd = int(np.sum(nums % 2 == 1))
        big = int(np.sum(nums >= BIG_THRESHOLD))
        result.append({
            "draw_num": r.get("draw_num"),
            "odd_even_ratio": f"{odd}:{n-odd}",
            "big_small_ratio": f"{big}:{n-big}",
        })
    return {"records": result}
