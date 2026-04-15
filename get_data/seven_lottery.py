import requests
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, BigInteger, Date, String
from sqlalchemy.types import SmallInteger
from model.seven_lottery import SevenLottery
from database import engine ,Base,SessionLocal


# ===================== 核心：清洗数字（把 - 变成 0）=====================
def clean_num(val):
    try:
        return int(val)
    except:
        return 0

# ===================== 数据抓取 =====================
url = "http://data.17500.cn/7xc_asc.txt"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_seven_lottery():
    """
    仅启动服务器时调用一次,用于初始化数据,重新加载数据
    :return:
    """
    db = SessionLocal()
    l = []
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        response.encoding = "gbk"
        text = response.text
        print("✅ 数据获取成功")

        lines = text.strip().splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 23:
                data = {
                    "issue": parts[0],
                    "draw_date": parts[1],
                    "number1": clean_num(parts[2]),
                    "number2": clean_num(parts[3]),
                    "number3": clean_num(parts[4]),
                    "number4": clean_num(parts[5]),
                    "number5": clean_num(parts[6]),
                    "number6": clean_num(parts[7]),
                    "number7": clean_num(parts[8]),
                    "total_sales": clean_num(parts[9]),
                    "prize_pool": clean_num(parts[10]),
                    "prize1_count": clean_num(parts[11]),
                    "prize1_amount": clean_num(parts[12]),
                    "prize2_count": clean_num(parts[13]),
                    "prize2_amount": clean_num(parts[14]),
                    "prize3_count": clean_num(parts[15]),
                    "prize3_amount": clean_num(parts[16]),
                    "prize4_count": clean_num(parts[17]),
                    "prize4_amount": clean_num(parts[18]),
                    "prize5_count": clean_num(parts[19]),
                    "prize5_amount": clean_num(parts[20]),
                    "prize6_count": clean_num(parts[21]),
                    "prize6_amount": clean_num(parts[22]),
                }
                l.append(SevenLottery(**data))

        print("✅ 数据处理完成，准备入库...")

        # 重建表
        Base.metadata.drop_all(bind=engine, tables=[SevenLottery.__table__])
        Base.metadata.create_all(bind=engine, tables=[SevenLottery.__table__])

        # 批量插入
        db.bulk_save_objects(l)
        db.commit()
        print(f"✅ 全部插入成功！共 {len(l)} 条数据")

    except Exception as e:
        db.rollback()
        print(f"❌ 出错：{e}")
    finally:
        db.close()


def day_get_seven_lottery():
    """
    每天获取数据
    :return:
    """
    pass


if __name__ == "__main__":
    get_seven_lottery()
