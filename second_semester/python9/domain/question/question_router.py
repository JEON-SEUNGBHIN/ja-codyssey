from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Question

router = APIRouter(
    prefix="/api/question",
    tags=["question"],
)


@router.get("/list")
def question_list(db: Session = Depends(get_db)):
    """
    SQLite에 저장된 Question 목록을 ORM으로 조회하여 반환한다.
    """
    questions = db.query(Question).all()
    return {
        "count": len(questions),
        "questions": [
            {
                "id": q.id,
                "subject": q.subject,
                "content": q.content,
                "create_date": q.create_date,
            }
            for q in questions
        ],
    }
