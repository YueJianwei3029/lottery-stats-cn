# -*- coding: utf-8 -*-
"""排列5 路由（含通用 + 扩展 + 高级统计）"""

from fastapi import APIRouter, Query
from app.core.database import db
from app.services.base_stats import base_stats
from app.services.pos_stats import (
    position_stats, digit_freq_stats, hot_cold_stats,
    ratio_stats, period_list_stats,
)
from app.services.advanced_stats import std_dev_stats, percentile_stats

router = APIRouter(prefix="/api/lottery_pl5", tags=["排列5"])

TABLE = "lottery_pl5"
FIELDS = ["num_1", "num_2", "num_3", "num_4", "num_5"]


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

@router.get("/stats/position")
def ext_position(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success",
            "data": position_stats(TABLE, FIELDS, date=date, end_date=end_date)}


@router.get("/stats/digit_freq")
def ext_digit_freq(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success",
            "data": digit_freq_stats(TABLE, FIELDS, date=date, end_date=end_date)}


@router.get("/stats/hot_cold")
def ext_hot_cold(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success",
            "data": hot_cold_stats(TABLE, FIELDS, date=date, end_date=end_date)}


@router.get("/stats/ratio")
def ext_ratio(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success",
            "data": ratio_stats(TABLE, FIELDS, date=date, end_date=end_date)}


@router.get("/stats/period_list")
def ext_period_list(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success",
            "data": period_list_stats(TABLE, FIELDS, date=date, end_date=end_date)}


# ========== 高级统计 ==========

@router.get("/stats/advanced/std")
def advanced_std(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success",
            "data": std_dev_stats(TABLE, date=date, end_date=end_date)}


@router.get("/stats/advanced/percentile")
def advanced_percentile(date: str = Query(default=None), end_date: str = Query(default=None)):
    return {"code": 200, "message": "success",
            "data": percentile_stats(TABLE, date=date, end_date=end_date)}
