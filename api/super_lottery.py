from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import get_db
from scheme.super_lottery import SuperLotteryResponse,PaginatedResponse
from crud.public import crud_count_lottery_numbers
from crud.super_lottery import (
    date_get_datas,get_all_number,
    get_all_front,
    crud_calculate_odd_even_big_small,
    crud_calculate_sum_span_statistics,
    crud_get_lottery_range_distribution)

# 依赖项,分页查询数据
from api.public import parse_date,pagination_show



# 定义子路由
super_lottery = APIRouter(prefix="/super_lottery", tags=["统计"])


# ===================== 数据获取 =====================
# id查询数据
# @super_lottery.get("/{id}", summary="查询数据",response_model=SuperLotteryResponse)
# async def get_super_lottery(id:int=10,db: Session = Depends(get_db)):
#     data=db.query(SuperLottery).filter(SuperLottery.id==id).first()
#     # print(data)
#     return data



# 分页查询指定时间到当前时间的数据信息
@super_lottery.get("/get/{date_str}",
                   response_model=PaginatedResponse[SuperLotteryResponse],
                   summary="分页查询指定时间到当前时间的数据信息")
async def get_datas(pages: int = 1, number: int = 10,
                    date_str: str = Depends(parse_date),
                    db: Session = Depends(get_db)
                    ):
    # 核心修改：添加 order_by(SuperLottery.draw_date.asc()) 按日期升序排序（最新->最早）
    datas = await date_get_datas(date_str,db)
    if not datas:
        return {"message": "无开奖数据"}
    return await pagination_show(datas,pages,number)


# ===================== 数据统计 =====================
# 1.指定时间到当前时间的各个区号数字的出现次数
@super_lottery.get("/count_lottery_numbers/{date_str}",
                   summary="指定时间到当前时间的各个区号数字的出现次数")
async def count_lottery_numbers(
        date_str: str = Depends(parse_date),
        db: Session = Depends(get_db)):
    # 返回查询数据信息
    # 定义位置名称
    positions = [
        "front1", "front2", "front3", "front4", "front5",
        "back1", "back2"
    ]
    data_list = await get_all_number(date_str,db)
    if not data_list:
        return {"message": "无开奖数据"}
    # 返回总统计结果
    result=await crud_count_lottery_numbers(data_list,positions)

    return {
        "total_draws": len(data_list),
        "number_counts": result
    }

# 2.计算前区号码的和值和跨度的统计信息
@super_lottery.get("/calculate_sum_span_statistics/{date_str}",
                   summary="计算前区号码的和值和跨度的统计信息")
async def calculate_sum_span_statistics(
        date_str: str = Depends(parse_date),
        db: Session = Depends(get_db)):

        data_list = await get_all_front(date_str,db)

        return await crud_calculate_sum_span_statistics(data_list)

# 3.计算前区号码的奇偶和大小的统计信息
@super_lottery.get("/calculate_odd_even_big_small/{date_str}",
                   summary="计算前区号码的奇偶和大小的统计信息")
async def calculate_odd_even_big_small(
        date_str: str = Depends(parse_date),
        db: Session = Depends(get_db)):
    # 只要询前区5个号码
    data_list = await get_all_front(date_str,db)

    if not data_list:
        return {"code": 404, "message": "无开奖数据", "data": None}
    # 获取奇偶和大小的统计信息
    return await crud_calculate_odd_even_big_small(data_list)



# 4.计算前区号码的区间分布统计信息
@super_lottery.get("/calculate_range_distribution/{date_str}",
                   summary="计算前区号码的区间分布统计信息")
async def get_lottery_range_distribution(
    date_str: str = Depends(parse_date),
    db: Session = Depends(get_db)):
    # 1. 查询前区5个号码
    data_list = await get_all_front(date_str,db)
    if not data_list:
        return {"code": 404, "msg": "未查询到开奖数据", "data": None}

    return await crud_get_lottery_range_distribution(data_list)


# ============= 独立测试启动代码（仅用于测试子路由）=============
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="测试子路由")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    # 关键：访问根目录html文件夹
    app.mount("/html", StaticFiles(directory="../html"), name="html")
    app.include_router(super_lottery)
    uvicorn.run(app, host="127.0.0.1", port=8080)
#     127.0.0.1:8080/html/super_lottery/index.html


