import numpy as np

# 统计每个位置 → 每个数字出现次数
async def crud_count_lottery_numbers(data_list,positions):
    # 转 numpy 数组（每行是一期开奖，每列是一个位置）
    arr = np.array(data_list)

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
