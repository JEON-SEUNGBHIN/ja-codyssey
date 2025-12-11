from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Question
from schemas import QuestionResponse, QuestionListResponse

router = APIRouter(
    prefix="/api/question",
    tags=["question"],
)


@router.get("/list", response_model=QuestionListResponse)
def question_list(db: Session = Depends(get_db)) -> QuestionListResponse:
    """
    SQLite에 저장된 Question 목록을 ORM으로 조회하여 반환한다.
    """
    questions = db.query(Question).all()

    return QuestionListResponse(
        count=len(questions),
        questions=[QuestionResponse.model_validate(q) for q in questions],
    )
