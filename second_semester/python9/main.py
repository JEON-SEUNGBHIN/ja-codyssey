"""
애플리케이션 진입점 (샘플)

Alembic 마이그레이션으로 테이블을 생성한 뒤,
테스트로 Question 레코드를 하나 넣어본다.
"""

from datetime import datetime

from database import SessionLocal
from models import Question


def create_sample_question():
    db = SessionLocal()
    try:
        q = Question(
            subject="첫 번째 질문",
            content="SQLAlchemy + Alembic 테스트 질문입니다.",
            create_date=datetime.utcnow(),
        )
        db.add(q)
        db.commit()
        db.refresh(q)

        print(f"생성된 질문: id={q.id}, subject={q.subject}, create_date={q.create_date}")
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_question()
