import numpy as np
from model.seven_lottery import SevenLottery



# 查询指定时间到当前时间的所有数据信息
async def date_get_datas(date_str,db):
    datas = (db.query(SevenLottery).
             filter(SevenLottery.draw_date >= date_str).
             order_by(SevenLottery.draw_date.desc()).all())
    return datas

# 根据日期时间查询【号码位置列】（号码1-7）的数据
async def get_all_number(date_str,db):
    query = db.query(
        SevenLottery.number1,
        SevenLottery.number2,
        SevenLottery.number3,
        SevenLottery.number4,
        SevenLottery.number5,
        SevenLottery.number6,
        SevenLottery.number7,
    ).filter(SevenLottery.draw_date >= date_str)  # 你的日期条件
    data_list = query.all()
    return data_list

