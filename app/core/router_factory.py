# -*- coding: utf-8 -*-
"""路由工厂：根据 LotteryConfig 自动生成完整的 APIRouter"""

import importlib
import logging
from dataclasses import dataclass, field
from fastapi import APIRouter, Query
from app.core.database import db
from app.services.base_stats import base_stats
from app.services.advanced_stats import std_dev_stats, percentile_stats, scatter_data, lln_data

logger = logging.getLogger(__name__)


@dataclass
class LotteryConfig:
    """描述一个彩种的差异配置"""
    key: str               # "dlt" | "ssq" | "7xc" | "pl5" | "pl3"
    table: str             # "lottery_dlt" | ...
    tag: str               # "超级大乐透" | ...
    num_fields: list       # 号码字段列表
    ext_module: str        # 扩展统计模块路径，如 "app.services.dlt_stats"
    uses_pos_stats: bool = False      # 是否使用 pos_stats (PL3/PL5)


class RouterFactory:
    """根据 LotteryConfig 自动生成完整的 APIRouter"""

    @staticmethod
    def build(config: LotteryConfig) -> APIRouter:
        table = config.table
        ext = importlib.import_module(config.ext_module)

        router = APIRouter(prefix=f"/api/{table}", tags=[config.tag])

        # ---- 通用：分页查询 ----
        @router.get("/query")
        def query(date: str = Query(default="20260101"),
                  end_date: str = Query(default=None),
                  page: int = Query(default=1, ge=1),
                  page_size: int = Query(default=20, ge=1, le=100)):
            return {"code": 200, "message": "success",
                    "data": db.query(table, date=date, end_date=end_date,
                                     page=page, page_size=page_size)}

        # ---- 通用：基础统计 ----
        @router.get("/stats")
        def stats(date: str = Query(default=None),
                  end_date: str = Query(default=None)):
            return {"code": 200, "message": "success",
                    "data": base_stats(table, date=date, end_date=end_date)}

        # ---- 扩展：position ----
        @router.get("/stats/position")
        def ext_position(date: str = Query(default=None),
                         end_date: str = Query(default=None)):
            if config.uses_pos_stats:
                data = ext.position_stats(table, config.num_fields,
                                          date=date, end_date=end_date)
            else:
                data = ext.position_stats(date=date, end_date=end_date)
            return {"code": 200, "message": "success", "data": data}

        # ---- 扩展：hot_cold ----
        @router.get("/stats/hot_cold")
        def ext_hot_cold(date: str = Query(default=None),
                         end_date: str = Query(default=None)):
            if config.uses_pos_stats:
                data = ext.hot_cold_stats(table, config.num_fields,
                                          date=date, end_date=end_date)
            else:
                data = ext.hot_cold_stats(date=date, end_date=end_date)
            return {"code": 200, "message": "success", "data": data}

        # ---- 扩展：period_list ----
        @router.get("/stats/period_list")
        def ext_period_list(date: str = Query(default=None),
                            end_date: str = Query(default=None)):
            if config.uses_pos_stats:
                data = ext.period_list_stats(table, config.num_fields,
                                             date=date, end_date=end_date)
            else:
                data = ext.period_list_stats(date=date, end_date=end_date)
            return {"code": 200, "message": "success", "data": data}

        # ---- 扩展：ratio ----
        @router.get("/stats/ratio")
        def ext_ratio(date: str = Query(default=None),
                      end_date: str = Query(default=None)):
            if config.uses_pos_stats:
                data = ext.ratio_stats(table, config.num_fields,
                                       date=date, end_date=end_date)
            else:
                data = ext.ratio_stats(date=date, end_date=end_date)
            return {"code": 200, "message": "success", "data": data}

        # ---- 高级：std ----
        @router.get("/stats/advanced/std")
        def advanced_std(date: str = Query(default=None),
                         end_date: str = Query(default=None)):
            return {"code": 200, "message": "success",
                    "data": std_dev_stats(table, date=date, end_date=end_date)}

        # ---- 高级：percentile ----
        @router.get("/stats/advanced/percentile")
        def advanced_percentile(date: str = Query(default=None),
                                end_date: str = Query(default=None)):
            return {"code": 200, "message": "success",
                    "data": percentile_stats(table, date=date, end_date=end_date)}

        # ---- 高级：scatter（散点图） ----
        @router.get("/stats/advanced/scatter")
        def advanced_scatter(date: str = Query(default=None),
                             end_date: str = Query(default=None),
                             limit: int = Query(default=500, ge=100, le=2000)):
            return {"code": 200, "message": "success",
                    "data": scatter_data(table, date=date, end_date=end_date, limit=limit)}

        # ---- 高级：lln（大数定律运行均值） ----
        @router.get("/stats/advanced/lln")
        def advanced_lln(date: str = Query(default=None),
                         end_date: str = Query(default=None),
                         limit: int = Query(default=500, ge=100, le=2000)):
            return {"code": 200, "message": "success",
                    "data": lln_data(table, date=date, end_date=end_date, limit=limit)}

        return router


# ============================================================
# 5 个彩种配置
# ============================================================

LOTTERY_CONFIGS = [
    LotteryConfig(
        key="dlt",
        table="lottery_dlt",
        tag="超级大乐透",
        num_fields=["front_1","front_2","front_3","front_4","front_5","back_1","back_2"],
        ext_module="app.services.dlt_stats",
    ),
    LotteryConfig(
        key="ssq",
        table="lottery_ssq",
        tag="双色球",
        num_fields=["red_1","red_2","red_3","red_4","red_5","red_6","blue_1"],
        ext_module="app.services.ssq_stats",
    ),
    LotteryConfig(
        key="7xc",
        table="lottery_7xc",
        tag="七星彩",
        num_fields=["num_1","num_2","num_3","num_4","num_5","num_6","back_1"],
        ext_module="app.services.qxc_stats",
    ),
    LotteryConfig(
        key="pl5",
        table="lottery_pl5",
        tag="排列5",
        num_fields=["num_1","num_2","num_3","num_4","num_5"],
        ext_module="app.services.pos_stats",
        uses_pos_stats=True,
    ),
    LotteryConfig(
        key="pl3",
        table="lottery_pl3",
        tag="排列3",
        num_fields=["num_1","num_2","num_3"],
        ext_module="app.services.pos_stats",
        uses_pos_stats=True,
    ),
]
