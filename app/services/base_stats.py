# -*- coding: utf-8 -*-
"""通用统计模块：号码频率、奇偶、大小（5 个彩种通用）- numpy 加速版"""

import logging
import numpy as np
from app.core.database import db
from app.core.numpy_utils import records_to_array

logger = logging.getLogger(__name__)

# ============================================================
# 各表号码字段映射与大小中位数
# ============================================================
TABLE_META = {
    "lottery_pl3": {
        "num_fields": ["num_1", "num_2", "num_3"],
        "big_threshold": 5,
        "range_min": 0,
        "range_max": 9,
    },
    "lottery_ssq": {
        "num_fields": ["red_1", "red_2", "red_3", "red_4", "red_5", "red_6", "blue_1"],
        "big_threshold_map": {
            "red_1": 17, "red_2": 17, "red_3": 17, "red_4": 17, "red_5": 17, "red_6": 17,
            "blue_1": 9,
        },
        "range_min": 1,
        "range_max": 33,
    },
    "lottery_pl5": {
        "num_fields": ["num_1", "num_2", "num_3", "num_4", "num_5"],
        "big_threshold": 5,
        "range_min": 0,
        "range_max": 9,
    },
    "lottery_7xc": {
        "num_fields": ["num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "back_1"],
        "big_threshold_map": {
            "num_1": 5, "num_2": 5, "num_3": 5, "num_4": 5, "num_5": 5, "num_6": 5,
            "back_1": 8,  # 0-14，中位数7，≥8为大
        },
        "range_min": 0,
        "range_max": 14,
    },
    "lottery_dlt": {
        "num_fields": ["front_1", "front_2", "front_3", "front_4", "front_5", "back_1", "back_2"],
        "big_threshold_map": {
            "front_1": 18, "front_2": 18, "front_3": 18, "front_4": 18, "front_5": 18,
            "back_1": 7, "back_2": 7,
        },
        "range_min": 1,
        "range_max": 35,
    },
}


def _get_big_threshold(field: str, meta: dict) -> int:
    """获取某字段的大小分界值"""
    if "big_threshold_map" in meta:
        return meta["big_threshold_map"].get(field, 5)
    return meta.get("big_threshold", 5)


def base_stats(table: str, date: str = None, end_date: str = None) -> dict:
    """
    通用基础统计（按位置拆分）

    :param table: 表名
    :param date: 起始日期 YYYYMMDD，None 表示全量
    :param end_date: 结束日期 YYYYMMDD
    :return: {
        "fields": ["num_1","num_2",...],
        "freq": {"num_1": {"0":200,"1":180,...}, "num_2":{...}},
        "odd_even": {"num_1": {"odd":1000,"even":1100}, ...},
        "big_small": {"num_1": {"big":1200,"small":900}, ...},
    }
    """
    meta = TABLE_META.get(table)
    if not meta:
        return {"fields": [], "freq": {}, "odd_even": {}, "big_small": {}}

    records = db.fetch_all(table, date=date, end_date=end_date)
    fields = meta["num_fields"]

    empty = {"fields": fields, "freq": {}, "odd_even": {}, "big_small": {}}
    if not records:
        return empty

    # numpy 加速：转换为二维数组
    arr = records_to_array(records, fields)

    freq = {}
    oe = {}
    bs = {}

    for i, field in enumerate(fields):
        col = arr[:, i]
        valid = col[~np.isnan(col)]

        # 频率统计
        values, counts = np.unique(valid, return_counts=True)
        freq[field] = {str(int(v)): int(c) for v, c in zip(values, counts) if not np.isnan(v)}

        # 频率按 key 排序
        freq[field] = dict(sorted(freq[field].items(), key=lambda x: int(x[0])))

        # 奇偶统计（向量化）
        odd_count = int(np.sum(valid % 2 == 1))
        even_count = int(np.sum(valid % 2 == 0))
        oe[field] = {"odd": odd_count, "even": even_count}

        # 大小统计（向量化）
        threshold = _get_big_threshold(field, meta)
        big_count = int(np.sum(valid >= threshold))
        small_count = int(np.sum(valid < threshold))
        bs[field] = {"big": big_count, "small": small_count}

    return {"fields": fields, "freq": freq, "odd_even": oe, "big_small": bs}
