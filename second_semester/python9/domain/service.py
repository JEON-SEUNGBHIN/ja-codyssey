"""
질문(Question) 도메인 서비스 로직

데이터베이스와의 CRUD 작업을 담당하는 서비스 레이어입니다.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from models import Question
from schemas import QuestionCreate, QuestionUpdate


def create_question(db: Session, question: QuestionCreate) -> Question:
    """
    새로운 질문을 생성합니다.
    
    Args:
        db: 데이터베이스 세션
        question: 생성할 질문 정보
        
    Returns:
        생성된 Question 객체
        
    Raises:
        Exception: 데이터베이스 작업 실패 시 롤백 후 예외 발생
    """
    try:
        db_question = Question(
            subject=question.subject,
            content=question.content
        )
        db.add(db_question)
        db.commit()  # 트랜잭션 커밋 (Durability 보장)
        db.refresh(db_question)  # DB에서 최신 데이터 조회
        return db_question
    except Exception:
        # 에러 발생 시 롤백하여 트랜잭션 원자성 보장 (Atomicity)
        db.rollback()
        raise


def get_question(db: Session, question_id: int) -> Optional[Question]:
    """
    ID로 질문을 조회합니다.
    
    Args:
        db: 데이터베이스 세션
        question_id: 조회할 질문의 ID
        
    Returns:
        Question 객체 또는 None
    """
    return db.query(Question).filter(Question.id == question_id).first()


def get_questions(db: Session, skip: int = 0, limit: int = 100) -> List[Question]:
    """
    질문 목록을 조회합니다.
    
    Args:
        db: 데이터베이스 세션
        skip: 건너뛸 레코드 수
        limit: 최대 조회할 레코드 수
        
    Returns:
        Question 객체 리스트
    """
    return db.query(Question).offset(skip).limit(limit).all()


def update_question(
    db: Session, 
    question_id: int, 
    question_update: QuestionUpdate
) -> Optional[Question]:
    """
    질문을 수정합니다.
    
    Args:
        db: 데이터베이스 세션
        question_id: 수정할 질문의 ID
        question_update: 수정할 내용
        
    Returns:
        수정된 Question 객체 또는 None
        
    Raises:
        Exception: 데이터베이스 작업 실패 시 롤백 후 예외 발생
    """
    try:
        db_question = get_question(db, question_id)
        if db_question is None:
            return None
        
        if question_update.subject is not None:
            db_question.subject = question_update.subject
        if question_update.content is not None:
            db_question.content = question_update.content
        
        db.commit()  # 트랜잭션 커밋 (Durability 보장)
        db.refresh(db_question)  # DB에서 최신 데이터 조회
        return db_question
    except Exception:
        # 에러 발생 시 롤백하여 트랜잭션 원자성 보장 (Atomicity)
        db.rollback()
        raise


def delete_question(db: Session, question_id: int) -> bool:
    """
    질문을 삭제합니다.
    
    Args:
        db: 데이터베이스 세션
        question_id: 삭제할 질문의 ID
        
    Returns:
        삭제 성공 여부
        
    Raises:
        Exception: 데이터베이스 작업 실패 시 롤백 후 예외 발생
    """
    try:
        db_question = get_question(db, question_id)
        if db_question is None:
            return False
        
        db.delete(db_question)
        db.commit()  # 트랜잭션 커밋 (Durability 보장)
        return True
    except Exception:
        # 에러 발생 시 롤백하여 트랜잭션 원자성 보장 (Atomicity)
        db.rollback()
        raise