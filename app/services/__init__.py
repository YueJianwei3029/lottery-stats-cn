# -*- coding: utf-8 -*-
"""统计服务模块入口"""

from app.services.base_stats import base_stats
from app.services import dlt_stats
from app.services import qxc_stats

__all__ = ["base_stats", "dlt_stats", "qxc_stats"]
