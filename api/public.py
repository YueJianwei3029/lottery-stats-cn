from datetime import datetime
from fastapi import HTTPException
import math

# 依赖项,解析日期字符串为日期对象,日期格式为YYYYMMDD(不加-号)
def parse_date(date_str: str="20260111"):
    try:
        return datetime.strptime(date_str, "%Y%m%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式应为YYYYMMDD")

async def pagination_show(datas,pages:int=1,number:int=10):
    total_items = len(datas)
    total_pages = math.ceil(total_items / number)
    start = (pages - 1) * number
    end = start + number
    paginated_datas = datas[start:end]
    return {
        "data": paginated_datas,
        "current_page": pages,
        "page_size": number,
        "total_pages": total_pages,
        "total_items": total_items
    }