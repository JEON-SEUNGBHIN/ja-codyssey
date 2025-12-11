from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from models import Question
from schemas import QuestionCreate, QuestionResponse, QuestionListResponse

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


@router.post(
    "/create",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def question_create(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    """
    새로운 질문을 등록한다.

    - POST 메서드 사용
    - Depends(get_db)를 통해 DB 세션 의존성 주입
    - SQLAlchemy ORM으로 Question 객체 생성 및 저장
    """
    question = Question(
        subject=payload.subject,
        content=payload.content,
        create_date=datetime.utcnow(),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return QuestionResponse.model_validate(question)
