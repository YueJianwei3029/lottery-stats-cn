from sqlalchemy import Column, Integer, BigInteger, Date, SmallInteger,String
from database import Base

class SuperLottery(Base):
    __tablename__ = 'super_lottery'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增主键')
    issue = Column(String(10), nullable=False, unique=True, comment='期号')
    draw_date = Column(Date, nullable=False, comment='开奖日期')
    front1 = Column(SmallInteger, nullable=False, comment='前区1')
    front2 = Column(SmallInteger, nullable=False, comment='前区2')
    front3 = Column(SmallInteger, nullable=False, comment='前区3')
    front4 = Column(SmallInteger, nullable=False, comment='前区4')
    front5 = Column(SmallInteger, nullable=False, comment='前区5')
    back1 = Column(SmallInteger, nullable=False, comment='后区1')
    back2 = Column(SmallInteger, nullable=False, comment='后区2')
    total_sales = Column(BigInteger, nullable=False, comment='总销量')
    prize_pool = Column(BigInteger, nullable=False, comment='奖池金额')
    prize1_count = Column(Integer, nullable=False, comment='一等奖注数')
    prize1_amount = Column(BigInteger, nullable=False, comment='一等奖奖金')
    prize2_count = Column(Integer, nullable=False, comment='二等奖注数')
    prize2_amount = Column(BigInteger, nullable=False, comment='二等奖奖金')
    prize3_count = Column(Integer, nullable=False, comment='三等奖注数')
    prize3_amount = Column(Integer, nullable=False, comment='三等奖奖金')
    prize4_count = Column(Integer, nullable=False, comment='四等奖注数')
    prize4_amount = Column(Integer, nullable=False, comment='四等奖奖金')
    prize5_count = Column(Integer, nullable=False, comment='五等奖注数')
    prize5_amount = Column(Integer, nullable=False, comment='五等奖奖金')
    prize6_count = Column(Integer, nullable=False, comment='六等奖注数')
    prize6_amount = Column(Integer, nullable=False, comment='六等奖奖金')
    prize7_count = Column(Integer, nullable=False, comment='七等奖注数')
    prize7_amount = Column(Integer, nullable=False, comment='七等奖奖金')
    prize8_count = Column(Integer, nullable=False, comment='八等奖注数')
    prize8_amount = Column(Integer, nullable=False, comment='八等奖奖金')
    prize9_count = Column(Integer, nullable=False, comment='九等奖注数')
    prize9_amount = Column(Integer, nullable=False, comment='九等奖奖金')

    __table_args__ = {
        'comment': '超级大乐透历史开奖数据',
        'mysql_charset': 'utf8mb4'
    }