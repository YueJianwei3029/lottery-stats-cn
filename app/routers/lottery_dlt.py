# -*- coding: utf-8 -*-
"""超级大乐透 路由（含通用 + 扩展统计）"""

from fastapi import APIRouter, Query
from app.core.database import db
from app.services.base_stats import base_stats
from app.services import dlt_stats as ext

router = APIRouter(prefix="/api/lottery_dlt", tags=["超级大乐透"])

TABLE = "lottery_dlt"


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


@router.get("/stats/area")
def stats_area(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.area_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/sum_span")
def stats_sum_span(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.sum_span_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/odd_even_size")
def stats_odd_even_size(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.odd_even_size_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/zone")
def stats_zone(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.zone_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}
