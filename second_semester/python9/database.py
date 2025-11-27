"""
데이터베이스 연결 설정 모듈
SQLite + SQLAlchemy ORM 설정
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# 프로젝트 루트에 board.db 파일 생성/접속
DATABASE_URL = "sqlite:///./board.db"

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,  # 디버깅 시 True로 변경 가능
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ORM 모델들이 상속할 Base 클래스
Base = declarative_base()


def get_db():
    """
    DB 세션을 제공하는 제너레이터 유틸 (주로 FastAPI에서 사용)
    여기서는 샘플 코드용으로만 사용 가능.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
