"""
데이터베이스 연결 설정 모듈
SQLite + SQLAlchemy ORM 설정
"""

from contextlib import contextmanager

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


@contextmanager
def db_session():
    """
    contextlib.contextmanager를 사용한 DB 세션 컨텍스트 매니저.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db():
    """
    FastAPI 의존성으로 사용할 DB 세션 제너레이터.

    내부에서 contextlib 기반 컨텍스트 매니저를 사용해
    세션을 열고, 사용 후 자동으로 닫는다.
    """
    with db_session() as db:
        yield db
