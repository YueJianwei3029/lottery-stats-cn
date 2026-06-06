# -*- coding: utf-8 -*-
"""排列5 路由"""

from fastapi import APIRouter, Query
from app.core.database import db
from app.services.base_stats import base_stats

router = APIRouter(prefix="/api/lottery_pl5", tags=["排列5"])

TABLE = "lottery_pl5"


@router.get("/query")
def query(
    date: str = Query(default="20260101", description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
):
    result = db.query(TABLE, date=date, end_date=end_date, page=page, page_size=page_size)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats")
def stats(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = base_stats(TABLE, date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}
