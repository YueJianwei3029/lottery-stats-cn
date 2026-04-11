from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api import super_lottery as sl
from get_data.super_lottery import get_super_lottery


app = FastAPI(title="super_lottery", version="1.0.0")
@app.get("/", summary="根路径")
async def root():
    return {"message": "服务运行正常"}

# ===================== 子路由 =====================
app.include_router(sl.super_lottery)

# ===================== 初始化数据库 =====================
get_super_lottery()
print("super_lottery数据初始化完成")

# ===================== 跨域 =====================!!
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ===================== 静态文件 =====================
# 关键：访问根目录html文件夹
app.mount("/html", StaticFiles(directory="./html"), name="html")

# ===================== 启动 =====================
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8080)
# 热重启
# uvicorn test_main:app --reload


