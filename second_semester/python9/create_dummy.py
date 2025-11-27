from datetime import datetime
from database import SessionLocal
from models import Question

db = SessionLocal()

q = Question(
    subject="샘플 질문",
    content="SQLite + ORM 테스트입니다.",
    create_date=datetime.utcnow()
)

db.add(q)
db.commit()
db.close()

print("샘플 데이터 1건 추가 완료")