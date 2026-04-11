import numpy as np

from model.super_lottery import SuperLottery


# 查询指定时间到当前时间的所有数据信息
async def date_get_datas(date_str,db):
    datas = (db.query(SuperLottery).
             filter(SuperLottery.draw_date >= date_str).
             order_by(SuperLottery.draw_date.desc()).all())
    return datas

# 根据日期时间查询【号码位置列】（前区1-5，后区1-2）的数据
async def get_all_number(date_str,db):
    query = db.query(
        SuperLottery.front1,
        SuperLottery.front2,
        SuperLottery.front3,
        SuperLottery.front4,
        SuperLottery.front5,
        SuperLottery.back1,
        SuperLottery.back2,
    ).filter(SuperLottery.draw_date >= date_str)  # 你的日期条件
    data_list = query.all()
    return data_list

# 根据日期时间查询【号码位置列】（前区1-5）的数据
async def get_all_front(date_str,db):
    query = db.query(
        SuperLottery.front1,
        SuperLottery.front2,
        SuperLottery.front3,
        SuperLottery.front4,
        SuperLottery.front5,
    ).filter(SuperLottery.draw_date >= date_str)  # 你的日期条件
    data_list = query.all()
    return data_list

# 统计每个位置 → 每个数字出现次数
async def crud_count_lottery_numbers(data_list):
    # 转 numpy 数组（每行是一期开奖，每列是一个位置）
    arr = np.array(data_list)

    # 定义位置名称
    positions = [
        "front1", "front2", "front3", "front4", "front5",
        "back1", "back2"
    ]

    # 统计每个位置 → 每个数字出现次数
    # enumerate(positions)：这是一个内置函数，用于将positions中的每个元素与其索引一起打包成一个元组
    # 例如(0, positions[0])，(1, positions[1])
    result = {}
    for idx, pos in enumerate(positions):
        # 取出当前位置的所有数字（整列）
        column_numbers = arr[:, idx]

        # 统计每个数字出现次数
        unique_nums, counts = np.unique(column_numbers, return_counts=True)

        # 转成字典：{数字: 次数}
        # zip()函数：将多个可迭代对象打包成元组序列，返回一个元组
        count_dict = dict(zip(unique_nums.tolist(), counts.tolist()))

        # 按数字从小到大排序
        # .items()方法：返回字典的键值对视图，按键排序
        sorted_count = dict(sorted(count_dict.items()))

        # 存储结果于字典中
        result[pos] = sorted_count
    return result

# 计算前区号码的和值和跨度的统计信息
async def crud_calculate_odd_even_big_small(data_list):
    # 转 numpy 数组
    arr = np.array(data_list)
    total = len(arr)

    # ======================
    # 3. 奇偶统计
    # ======================
    odd_count = np.sum(arr % 2 == 1, axis=1)
    even_count = 5 - odd_count

    odd_even_pairs = [f"{o}:{e}" for o, e in zip(odd_count, even_count)]
    unique_oe, oe_counts = np.unique(odd_even_pairs, return_counts=True)

    # ✅ 修复：转成 Python int
    odd_even_dist: Dict[str, int] = {
        str(k): int(v) for k, v in zip(unique_oe, oe_counts)
    }
    odd_even_sorted = dict(sorted(odd_even_dist.items(), key=lambda x: x[1], reverse=True))

    # ======================
    # 大小统计
    # ======================
    big_count = np.sum(arr > 18, axis=1)
    small_count = 5 - big_count

    big_small_pairs = [f"{b}:{s}" for b, s in zip(big_count, small_count)]
    unique_bs, bs_counts = np.unique(big_small_pairs, return_counts=True)

    # ✅ 修复：转成 Python int
    big_small_dist: Dict[str, int] = {
        str(k): int(v) for k, v in zip(unique_bs, bs_counts)
    }
    big_small_sorted = dict(sorted(big_small_dist.items(), key=lambda x: x[1], reverse=True))
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total_draws": total,
            "odd_even_distribution": odd_even_sorted,
            "big_small_distribution": big_small_sorted
        }
    }

# 计算前区号码的奇偶和大小的统计信息
async def crud_calculate_sum_span_statistics(data_list):
    if not data_list:
        return {"message": "无开奖数据"}

    # 2. 转numpy数组（每行 = 一期前区5个号）
    arr = np.array(data_list)

    # ======================
    # 3. 计算 每期 和值
    # ======================
    sum_values = np.sum(arr, axis=1)  # 每行求和 → 和值数组

    # 统计每个和值出现次数
    unique_sum, sum_counts = np.unique(sum_values, return_counts=True)
    sum_dict = dict(zip(unique_sum.tolist(), sum_counts.tolist()))
    sorted_sum = dict(sorted(sum_dict.items()))  # 按和值从小到大排序

    # 和值范围
    sum_min = int(np.min(sum_values))
    sum_max = int(np.max(sum_values))
    sum_avg = round(float(np.mean(sum_values)), 2)

    # ======================
    # 4. 计算 每期 跨度
    # ======================
    span_values = np.max(arr, axis=1) - np.min(arr, axis=1)  # 每行最大值 - 最小值

    # 统计每个跨度出现次数
    unique_span, span_counts = np.unique(span_values, return_counts=True)
    span_dict = dict(zip(unique_span.tolist(), span_counts.tolist()))
    sorted_span = dict(sorted(span_dict.items()))  # 按跨度从小到大排序

    # 跨度范围
    span_min = int(np.min(span_values))
    span_max = int(np.max(span_values))
    span_avg = round(float(np.mean(span_values)), 2)

    # ======================
    # 5. 组装最终结果
    # ======================
    return {
        "total_draws": len(data_list),
        "sum_statistics": {
            "sum_range": f"{sum_min} ~ {sum_max}",
            "average_sum": sum_avg,
            "sum_frequency": sorted_sum  # 每个和值出现多少次
        },
        "span_statistics": {
            "span_range": f"{span_min} ~ {span_max}",
            "average_span": span_avg,
            "span_frequency": sorted_span  # 每个跨度出现多少次
        }
    }

# 计算前区号码的区间分布统计信息
async def crud_get_lottery_range_distribution(data_list):
    # 2. 转为 numpy 数组
    arr = np.array(data_list)
    total_draws = len(arr)

    # 3. 三区统计（1-11, 12-22, 23-35）
    range1 = np.sum((arr >= 1) & (arr <= 11), axis=1)
    range2 = np.sum((arr >= 12) & (arr <= 22), axis=1)
    range3 = np.sum((arr >= 23) & (arr <= 35), axis=1)

    # 4. 组合区间形态（如 2:2:1）
    range_combinations = [f"{a}:{b}:{c}" for a, b, c in zip(range1, range2, range3)]
    unique_combs, comb_counts = np.unique(range_combinations, return_counts=True)
    range_freq = dict(zip(unique_combs, comb_counts.tolist()))

    # 按出现次数降序排序
    range_freq_sorted = dict(sorted(range_freq.items(), key=lambda x: x[1], reverse=True))

    # 5. 各区间总出号数
    total_range1 = int(np.sum(range1))
    total_range2 = int(np.sum(range2))
    total_range3 = int(np.sum(range3))

    # 6. 返回统一格式接口数据
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total_draws": total_draws,
            "range_definition": "一区:1-11 | 二区:12-22 | 三区:23-35",
            "range_combination_frequency": range_freq_sorted,
            "total_numbers_in_range": {
                "range1_total": total_range1,
                "range2_total": total_range2,
                "range3_total": total_range3
            }
        }
    }

