from sqlalchemy import Column, Integer, BigInteger, Date, SmallInteger, String
from datetime import date
from pydantic import BaseModel, field_serializer
from typing import List,Generic,TypeVar


class SuperLotteryResponse(BaseModel):
    issue: str = Column(String, nullable=False, unique=True, comment='期号')
    draw_date: date = Column(Date, nullable=False, comment='开奖日期')
    front1: int = Column(SmallInteger, nullable=False, comment='前区1')
    front2: int = Column(SmallInteger, nullable=False, comment='前区2')
    front3: int = Column(SmallInteger, nullable=False, comment='前区3')
    front4: int = Column(SmallInteger, nullable=False, comment='前区4')
    front5: int = Column(SmallInteger, nullable=False, comment='前区5')
    back1: int = Column(SmallInteger, nullable=False, comment='后区1')
    back2: int = Column(SmallInteger, nullable=False, comment='后区2')
    total_sales: int = Column(BigInteger, nullable=False, comment='总销量')
    prize_pool: int = Column(BigInteger, nullable=False, comment='奖池金额')
    prize1_count: int = Column(Integer, nullable=False, comment='一等奖注数')
    prize1_amount: int = Column(BigInteger, nullable=False, comment='一等奖奖金')
    prize2_count: int = Column(Integer, nullable=False, comment='二等奖注数')
    prize2_amount: int = Column(BigInteger, nullable=False, comment='二等奖奖金')
    prize3_count: int = Column(Integer, nullable=False, comment='三等奖注数')
    prize3_amount: int = Column(Integer, nullable=False, comment='三等奖奖金')
    prize4_count: int = Column(Integer, nullable=False, comment='四等奖注数')
    prize4_amount: int = Column(Integer, nullable=False, comment='四等奖奖金')
    prize5_count: int = Column(Integer, nullable=False, comment='五等奖注数')
    prize5_amount: int = Column(Integer, nullable=False, comment='五等奖奖金')
    prize6_count: int = Column(Integer, nullable=False, comment='六等奖注数')
    prize6_amount: int = Column(Integer, nullable=False, comment='六等奖奖金')
    prize7_count: int = Column(Integer, nullable=False, comment='七等奖注数')
    prize7_amount: int = Column(Integer, nullable=False, comment='七等奖奖金')
    prize8_count: int = Column(Integer, nullable=False, comment='八等奖注数')
    prize8_amount: int = Column(Integer, nullable=False, comment='八等奖奖金')
    prize9_count: int = Column(Integer, nullable=False, comment='九等奖注数')
    prize9_amount: int = Column(Integer, nullable=False, comment='九等奖奖金')

    @field_serializer('draw_date')
    def serialize_draw_date(self, value: date) -> str:
        return value.strftime("%Y-%m-%d") if value else None

T = TypeVar('T')
class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    current_page: int
    page_size: int
    total_pages: int
    total_items: int