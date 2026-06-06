# -*- coding: utf-8 -*-
"""七乐彩 路由（含通用 + 扩展统计）"""

from fastapi import APIRouter, Query
from app.core.database import db
from app.services.base_stats import base_stats
from app.services import qxc_stats as ext

router = APIRouter(prefix="/api/lottery_7xc", tags=["七星彩"])

TABLE = "lottery_7xc"


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


@router.get("/stats/position")
def stats_position(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.position_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/period_list")
def stats_period_list(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.period_list_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/digit_freq")
def stats_digit_freq(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.digit_freq_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/hot_cold")
def stats_hot_cold(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.hot_cold_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/ratio")
def stats_ratio(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.ratio_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats/trend")
def stats_trend(
    date: str = Query(default=None, description="起始日期 YYYYMMDD"),
    end_date: str = Query(default=None, description="结束日期 YYYYMMDD"),
):
    result = ext.trend_stats(date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}
