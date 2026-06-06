# -*- coding: utf-8 -*-
"""超级大乐透 路由（含通用 + 扩展 + 高级统计）"""

from fastapi import APIRouter, Query
from app.core.database import db
from app.services.base_stats import base_stats
from app.services import dlt_stats as ext
from app.services.advanced_stats import std_dev_stats, percentile_stats, normal_dist_stats

router = APIRouter(prefix="/api/lottery_dlt", tags=["超级大乐透"])

TABLE = "lottery_dlt"


@router.get("/query")
def query(
    date: str = Query(default="20260101"),
    end_date: str = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    result = db.query(TABLE, date=date, end_date=end_date, page=page, page_size=page_size)
    return {"code": 200, "message": "success", "data": result}


@router.get("/stats")
def stats(date: str = Query(default=None), end_date: str = Query(default=None)):
    result = base_stats(TABLE, date=date, end_date=end_date)
    return {"code": 200, "message": "success", "data": result}


# ========== 扩展统计 ==========

@router.get("/stats/area")
def stats_area(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success", "data": ext.area_stats(date=date, end_date=end_date)}


@router.get("/stats/sum_span")
def stats_sum_span(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success", "data": ext.sum_span_stats(date=date, end_date=end_date)}


@router.get("/stats/odd_even_size")
def stats_odd_even_size(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success", "data": ext.odd_even_size_stats(date=date, end_date=end_date)}


@router.get("/stats/zone")
def stats_zone(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success", "data": ext.zone_stats(date=date, end_date=end_date)}


# ========== 高级统计 ==========

@router.get("/stats/advanced/std")
def advanced_std(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success", "data": std_dev_stats(TABLE, date=date, end_date=end_date)}


@router.get("/stats/advanced/percentile")
def advanced_percentile(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success", "data": percentile_stats(TABLE, date=date, end_date=end_date)}


@router.get("/stats/advanced/normal")
def advanced_normal(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success", "data": normal_dist_stats(TABLE, date=date, end_date=end_date)}
