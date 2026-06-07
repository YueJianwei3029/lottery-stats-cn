# -*- coding: utf-8 -*-
"""numpy 工具模块：所有 service 共用的 records→ndarray 转换

抽取自 6 个 service 文件中的 _records_to_array 函数。
"""

import numpy as np


def records_to_array(records, fields):
    """
    将记录列表(list[dict])转换为 numpy 二维数组，None 转为 NaN。

    :param records: list[dict]
    :param fields: 字段名列表
    :return: np.ndarray, shape=(len(records), len(fields))
    """
    data = []
    for r in records:
        row = [r.get(f) if r.get(f) is not None else np.nan for f in fields]
        data.append(row)
    return np.array(data, dtype=float)
