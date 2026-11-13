import os
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from datetime import date, datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///employees.db")

USE_SQLITE_FILE = DATABASE_URL.startswith("sqlite") and "mode=memory" not in DATABASE_URL
connect_args = {"check_same_thread": False} if USE_SQLITE_FILE else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    emp_no = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(64), nullable=False)
    department = Column(String(64), nullable=False)
    position = Column(String(64), default="")
    phone = Column(String(20), default="")
    hire_date = Column(Date, nullable=False)
    status = Column(String(16), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


_SEEDED = False


def init_db():
    """启动时建表"""
    global _SEEDED
    Base.metadata.create_all(bind=engine)
    if _SEEDED:
        return
    session = SessionFactory()
    try:
        if session.query(Employee).count() == 0:
            seeds = [
                ("EMP001", "张伟", "技术部", "后端工程师", "13800000001", date(2022, 3, 1), "active"),
                ("EMP002", "李娜", "技术部", "前端工程师", "13800000002", date(2021, 7, 15), "active"),
                ("EMP003", "王芳", "人事部", "HR经理", "13800000003", date(2020, 5, 10), "active"),
                ("EMP004", "刘洋", "财务部", "会计", "13800000004", date(2023, 1, 20), "active"),
                ("EMP005", "陈静", "技术部", "测试工程师", "13800000005", date(2022, 9, 5), "active"),
                ("EMP006", "杨波", "市场部", "市场专员", "13800000006", date(2023, 6, 12), "active"),
                ("EMP007", "赵敏", "人事部", "招聘专员", "13800000007", date(2021, 11, 1), "active"),
                ("EMP008", "周涛", "技术部", "架构师", "13800000008", date(2019, 4, 23), "active"),
                ("EMP009", "吴敏", "财务部", "出纳", "13800000009", date(2022, 12, 1), "active"),
                ("EMP010", "郑凯", "市场部", "市场总监", "13800000010", date(2018, 8, 30), "active"),
                ("EMP011", "孙丽", "技术部", "运维工程师", "13800000011", date(2023, 3, 17), "active"),
                ("EMP012", "马超", "人事部", "培训专员", "13800000012", date(2022, 6, 20), "resigned"),
                ("EMP013", "朱琳", "财务部", "财务经理", "13800000013", date(2020, 10, 8), "active"),
            ]
            for no, name, dept, pos, phone, hd, st in seeds:
                session.add(Employee(emp_no=no, name=name, department=dept, position=pos,
                                     phone=phone, hire_date=hd, status=st))
            session.commit()
        _SEEDED = True
    finally:
        session.close()
