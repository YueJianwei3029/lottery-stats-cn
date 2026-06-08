# -*- coding: utf-8 -*-
"""彩种爬虫工厂：根据 key 动态创建 Crawler 类

设计目的：
- 消除 5 个 *_crawler.py 文件中的模板重复
- 5 个子类（Pl3Crawler / SsqCrawler / ...）结构完全相同，
  仅 url/encoding 不同。改为统一的工厂函数。

对外保持原类名（Pl3Crawler / SsqCrawler / Pl5Crawler / QxcCrawler / DltCrawler），
不改动任何调用方代码。
"""

from app.crawler.base_crawler import BaseCrawler
from app.core.config import DATA_SOURCES


def make_crawler(table_key: str) -> type:
    """
    工厂函数：根据表名 key（如 'lottery_pl3'）动态生成 Crawler 子类。

    :param table_key: DATA_SOURCES 中的 key
    :return: BaseCrawler 子类（类名按 key 推导）
    """
    if table_key not in DATA_SOURCES:
        raise ValueError(f"Unknown lottery table key: {table_key}")

    cfg = DATA_SOURCES[table_key]
    # 类名推导：lottery_pl3 -> Pl3Crawler, lottery_7xc -> QxcCrawler
    short = table_key.replace("lottery_", "")
    cls_name = _SHORT_TO_CLASS_NAME.get(short, short.upper() + "Crawler")

    def _url(self) -> str:
        return cfg["url"]

    def _encoding(self) -> str:
        return cfg["encoding"]

    new_cls = type(
        cls_name,
        (BaseCrawler,),
        {
            "url": property(_url),
            "encoding": property(_encoding),
            "__module__": __name__,
        },
    )
    return new_cls


# 短名 -> 类名映射（兼容历史命名）
_SHORT_TO_CLASS_NAME = {
    "pl3": "Pl3Crawler",
    "ssq": "SsqCrawler",
    "pl5": "Pl5Crawler",
    "7xc": "QxcCrawler",   # 历史命名：七乐彩类叫 QxcCrawler
    "dlt": "DltCrawler",
}


# 对外暴露 5 个具体类（保持原导入路径兼容）
Pl3Crawler = make_crawler("lottery_pl3")
SsqCrawler = make_crawler("lottery_ssq")
Pl5Crawler = make_crawler("lottery_pl5")
QxcCrawler = make_crawler("lottery_7xc")
DltCrawler = make_crawler("lottery_dlt")
