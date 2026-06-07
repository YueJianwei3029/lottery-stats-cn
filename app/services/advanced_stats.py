# -*- coding: utf-8 -*-
"""高级统计服务：标准差、分位数、正态分布拟合、散点图、大数定律 - numpy 加速版"""

import logging
import numpy as np
from app.core.database import db

logger = logging.getLogger(__name__)

# 各彩种字段
TABLE_FIELDS = {
    "lottery_pl3": ["num_1", "num_2", "num_3"],
    "lottery_pl5": ["num_1", "num_2", "num_3", "num_4", "num_5"],
    "lottery_ssq": ["red_1", "red_2", "red_3", "red_4", "red_5", "red_6", "blue_1"],
    "lottery_7xc": ["num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "num_7"],
    "lottery_dlt": ["front_1", "front_2", "front_3", "front_4", "front_5", "back_1", "back_2"],
}

# 各位置的理论均值
#  数字型按均匀分布 (min+max)/2
#  组合型按次序统计量期望: E[X_(k)] = k×(N+1)/(n+1)  for k-th smallest of n draws from 1..N
EXPECTED_AVG = {
    "lottery_pl3": [4.5, 4.5, 4.5],
    "lottery_pl5": [4.5, 4.5, 4.5, 4.5, 4.5],
    "lottery_ssq": [
        round(1*34/7, 2), round(2*34/7, 2), round(3*34/7, 2),
        round(4*34/7, 2), round(5*34/7, 2), round(6*34/7, 2),
        8.5,  # blue
    ],
    "lottery_7xc": [4.5]*7,
    "lottery_dlt": [
        round(1*36/6, 1), round(2*36/6, 1), round(3*36/6, 1),
        round(4*36/6, 1), round(5*36/6, 1),               # front
        round(1*13/3, 2), round(2*13/3, 2),                # back
    ],
}


def _records_to_array(records, fields):
    data = []
    for r in records:
        row = []
        for f in fields:
            v = r.get(f)
            row.append(v if v is not None else np.nan)
        data.append(row)
    return np.array(data, dtype=float)


def std_dev_stats(table: str, date=None, end_date=None) -> dict:
    """各位置号码标准差 + 均值"""
    fields = TABLE_FIELDS.get(table, [])
    if not fields:
        return {"fields": [], "stats": []}

    records = db.fetch_all(table, date=date, end_date=end_date)
    if not records:
        return {"fields": fields, "stats": []}

    arr = _records_to_array(records, fields)
    stats = []

    for i, f in enumerate(fields):
        col = arr[:, i]
        valid = col[~np.isnan(col)]
        if len(valid) == 0:
            stats.append({"field": f, "mean": 0, "std": 0, "min": 0, "max": 0})
        else:
            mean_val = round(float(np.mean(valid)), 2)
            std_val = round(float(np.std(valid, ddof=1)), 2)
            stats.append({
                "field": f,
                "mean": mean_val,
                "std": std_val,
                "min": int(np.min(valid)),
                "max": int(np.max(valid)),
            })

    return {"fields": fields, "stats": stats}


def percentile_stats(table: str, date=None, end_date=None) -> dict:
    """各位置 P25/P50/P75 分位数"""
    fields = TABLE_FIELDS.get(table, [])
    if not fields:
        return {"fields": [], "stats": []}

    records = db.fetch_all(table, date=date, end_date=end_date)
    if not records:
        return {"fields": fields, "stats": []}

    arr = _records_to_array(records, fields)
    stats = []

    for i, f in enumerate(fields):
        col = arr[:, i]
        valid = col[~np.isnan(col)]
        if len(valid) == 0:
            stats.append({"field": f, "p25": 0, "p50": 0, "p75": 0})
        else:
            stats.append({
                "field": f,
                "p25": int(np.percentile(valid, 25)),
                "p50": int(np.percentile(valid, 50)),
                "p75": int(np.percentile(valid, 75)),
            })

    return {"fields": fields, "stats": stats}


def normal_dist_stats(table: str, date=None, end_date=None) -> dict:
    """正态分布拟合：偏度/峰度 + 直方图数据"""
    fields = TABLE_FIELDS.get(table, [])
    if not fields:
        return {"fields": [], "stats": []}

    records = db.fetch_all(table, date=date, end_date=end_date)
    if not records:
        return {"fields": fields, "stats": []}

    arr = _records_to_array(records, fields)
    stats = []

    for i, f in enumerate(fields):
        col = arr[:, i]
        valid = col[~np.isnan(col)]
        if len(valid) < 2:
            stats.append({"field": f, "mean": 0, "std": 0, "skewness": 0, "kurtosis": 0,
                          "histogram": {"bins": [], "counts": []}})
            continue

        mean_val = np.mean(valid)
        std_val = np.std(valid, ddof=1)
        if std_val == 0:
            skewness = 0.0
            kurtosis = 0.0
        else:
            z = (valid - mean_val) / std_val
            skewness = round(float(np.mean(z ** 3)), 3)
            kurtosis = round(float(np.mean(z ** 4) - 3), 3)

        # 直方图
        n_bins = min(15, max(5, int(len(valid) ** 0.5)))
        hist_counts, hist_edges = np.histogram(valid, bins=n_bins)
        hist_bins = [round((hist_edges[j] + hist_edges[j + 1]) / 2, 1) for j in range(n_bins)]

        stats.append({
            "field": f,
            "mean": round(float(mean_val), 2),
            "std": round(float(std_val), 2),
            "skewness": skewness,
            "kurtosis": kurtosis,
            "histogram": {"bins": hist_bins, "counts": [int(c) for c in hist_counts]},
        })

    return {"fields": fields, "stats": stats}


# ============================================================
# 散点图 + 大数定律
# ============================================================

def scatter_data(table: str, date=None, end_date=None, limit=500) -> dict:
    """散点图数据：每位置每期的数值，用于观察分布"""

    fields = TABLE_FIELDS.get(table, [])
    if not fields:
        return {"fields": [], "positions": {}}

    records = db.fetch_all(table, date=date, end_date=end_date)
    if not records:
        return {"fields": fields, "positions": {}}

    records_sorted = sorted(records, key=lambda r: r.get("draw_num", ""))
    if not date and not end_date:
        records_sorted = records_sorted[-limit:]

    positions = {}
    for i, f in enumerate(fields):
        pos_name = "第%d位" % (i + 1)
        points = []
        for idx, r in enumerate(records_sorted):
            v = r.get(f)
            if v is not None:
                points.append({
                    "index": idx + 1,
                    "draw_num": r.get("draw_num", ""),
                    "draw_date": _fmt(r.get("draw_date")),
                    "value": int(v),
                })
        positions[pos_name] = points

    return {"fields": fields, "positions": positions}


def lln_data(table: str, date=None, end_date=None, limit=500) -> dict:
    """大数定律 + 正态分布置信带：运行均值 + 逐期标准差 ±1σ/±2σ"""

    fields = TABLE_FIELDS.get(table, [])
    expected_avgs = EXPECTED_AVG.get(table, [])
    if not fields:
        return {"fields": [], "positions": {}}

    records = db.fetch_all(table, date=date, end_date=end_date)
    if not records:
        return {"fields": fields, "positions": {}}

    records_sorted = sorted(records, key=lambda r: r.get("draw_num", ""))
    if not date and not end_date:
        records_sorted = records_sorted[-limit:]

    positions = {}
    for i, f in enumerate(fields):
        pos_name = "第%d位" % (i + 1)
        expected = expected_avgs[i] if i < len(expected_avgs) else 0

        # 提取该位置的值序列
        values = np.array([int(r[f]) for r in records_sorted if r.get(f) is not None], dtype=float)
        n = len(values)
        if n == 0:
            positions[pos_name] = []
            continue

        # 向量化累计计算
        cum_sum = np.cumsum(values)
        cum_sq = np.cumsum(values ** 2)
        indices = np.arange(1, n + 1)
        running_avg = cum_sum / indices
        # 样本标准差: σ = sqrt((Σx²/n - (Σx/n)²) * n/(n-1))
        running_var = (cum_sq / indices - running_avg ** 2) * indices / np.maximum(indices - 1, 1)
        running_std = np.sqrt(np.maximum(running_var, 0))
        se = running_std / np.sqrt(indices)  # 标准误差

        points = []
        for idx in range(n):
            points.append({
                "index": int(indices[idx]),
                "draw_num": records_sorted[idx].get("draw_num", ""),
                "draw_date": _fmt(records_sorted[idx].get("draw_date")),
                "running_avg": round(float(running_avg[idx]), 4),
                "expected_avg": expected,
                "std": round(float(running_std[idx]), 2),
                "upper_1sigma": round(float(running_avg[idx] + se[idx]), 4),
                "lower_1sigma": round(float(running_avg[idx] - se[idx]), 4),
                "upper_2sigma": round(float(running_avg[idx] + 2 * se[idx]), 4),
                "lower_2sigma": round(float(running_avg[idx] - 2 * se[idx]), 4),
            })
        positions[pos_name] = points

    return {"fields": fields, "positions": positions}


def _fmt(d):
    if d is None:
        return ""
    if hasattr(d, "isoformat"):
        return d.isoformat()[:10]
    return str(d)[:10]
