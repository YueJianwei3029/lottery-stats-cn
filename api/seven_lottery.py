from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import get_db
from crud.seven_lottery import date_get_datas,get_all_number
from scheme.seven_lottery import SevenLotteryResponse,PaginatedResponse
from crud.public import crud_count_lottery_numbers

# 依赖项,分页查询数据
from api.public import parse_date,pagination_show

# 定义子路由
seven_lottery = APIRouter(prefix="/seven_lottery", tags=["统计"])


# 分页查询指定时间到当前时间的数据信息
@seven_lottery.get("/get/{date_str}",
                   response_model=PaginatedResponse[SevenLotteryResponse],
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
@seven_lottery.get("/count_lottery_numbers/{date_str}",
                   summary="指定时间到当前时间的各个区号数字的出现次数")
async def count_lottery_numbers(
        date_str: str = Depends(parse_date),
        db: Session = Depends(get_db)):
    # 返回查询数据信息
    # 定义位置名称
    positions = [
        "number1", "number2", "number3", "number4", "number5",
        "number6", "number7"
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
    app.include_router(seven_lottery)
    uvicorn.run(app, host="127.0.0.1", port=8080)
#   127.0.0.1:8080/html/seven_lottery/index.html

