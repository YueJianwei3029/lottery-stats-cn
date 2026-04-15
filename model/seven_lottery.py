from sqlalchemy import Column, Integer, BigInteger, Date, SmallInteger,String
from database import Base

class SevenLottery(Base):
    __tablename__ = 'seven_lottery'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='自增主键')
    issue = Column(String(10), nullable=False, unique=True, comment='期号')
    draw_date = Column(Date, nullable=False, comment='开奖日期')
    number1 = Column(SmallInteger, nullable=False, comment='1')
    number2 = Column(SmallInteger, nullable=False, comment='2')
    number3 = Column(SmallInteger, nullable=False, comment='3')
    number4 = Column(SmallInteger, nullable=False, comment='4')
    number5 = Column(SmallInteger, nullable=False, comment='5')
    number6 = Column(SmallInteger, nullable=False, comment='6')
    number7 = Column(SmallInteger, nullable=False, comment='7')
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


    __table_args__ = {
        'comment': '超级大乐透历史开奖数据',
        'mysql_charset': 'utf8mb4'
    }