"""
SQLAlchemy ORM 모델 정의 모듈
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class Question(Base):
    """
    질문 테이블 모델

    컬럼:
    - id: 질문 데이터의 고유번호 (Primary Key)
    - subject: 질문 제목
    - content: 질문 내용
    - create_date: 질문 작성일시
    """
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    create_date = Column(DateTime, default=datetime.utcnow, nullable=False)
