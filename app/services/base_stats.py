# -*- coding: utf-8 -*-
"""通用统计模块：号码频率、奇偶、大小（5 个彩种通用）"""

import logging
from app.core.database import db

logger = logging.getLogger(__name__)

# ============================================================
# 各表号码字段映射与大小中位数
# ============================================================
TABLE_META = {
    "lottery_pl3": {
        "num_fields": ["num_1", "num_2", "num_3"],
        "big_threshold": 5,   # >=5 为大，0-4 为小
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
        "num_fields": ["num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "num_7"],
        "big_threshold": 5,   # 0-9, >=5 为大
        "range_min": 0,
        "range_max": 9,
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

    # 初始化
    freq = {f: {} for f in fields}
    oe = {f: {"odd": 0, "even": 0} for f in fields}
    bs = {f: {"big": 0, "small": 0} for f in fields}

    for r in records:
        for field in fields:
            val = r.get(field)
            if val is None:
                continue

            # 频率
            k = str(val)
            freq[field][k] = freq[field].get(k, 0) + 1

            # 奇偶
            if val % 2 == 1:
                oe[field]["odd"] += 1
            else:
                oe[field]["even"] += 1

            # 大小
            threshold = _get_big_threshold(field, meta)
            if val >= threshold:
                bs[field]["big"] += 1
            else:
                bs[field]["small"] += 1

    # 频率排序
    for f in fields:
        freq[f] = dict(sorted(freq[f].items(), key=lambda x: int(x[0])))

    return {"fields": fields, "freq": freq, "odd_even": oe, "big_small": bs}
