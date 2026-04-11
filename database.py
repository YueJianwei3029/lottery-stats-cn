from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base


# ===================== 数据库配置 =====================
DATABASE_URL = "mysql+pymysql://root:123456@localhost/my_data_17500"
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
)

# 数据库模型
Base = declarative_base()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()