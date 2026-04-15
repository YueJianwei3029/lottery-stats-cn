from sqlalchemy import Column, Integer, BigInteger, Date, SmallInteger, String
from datetime import date
from pydantic import BaseModel, field_serializer
from typing import List,Generic,TypeVar


class SevenLotteryResponse(BaseModel):
    issue: str = Column(String, nullable=False, unique=True, comment='期号')
    draw_date: date = Column(Date, nullable=False, comment='开奖日期')
    number1: int = Column(SmallInteger, nullable=False, comment='号码1')
    number2: int = Column(SmallInteger, nullable=False, comment='号码2')
    number3: int = Column(SmallInteger, nullable=False, comment='号码3')
    number4: int = Column(SmallInteger, nullable=False, comment='号码4')
    number5: int = Column(SmallInteger, nullable=False, comment='号码5')
    number6: int = Column(SmallInteger, nullable=False, comment='号码6')
    number7: int = Column(SmallInteger, nullable=False, comment='号码7')
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