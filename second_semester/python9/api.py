"""
FastAPI 라우터 정의

질문(Question)에 대한 CRUD API 엔드포인트를 정의합니다.
"""
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import (
    QuestionCreate, 
    QuestionUpdate, 
    QuestionResponse, 
    QuestionListResponse,
    ApiResponse
)
from domain.service import (
    create_question,
    get_question,
    get_questions,
    update_question,
    delete_question
)

router = APIRouter()


@router.post('/questions', response_model=ApiResponse, status_code=201)
def create_question_endpoint(
    question: QuestionCreate,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    새로운 질문을 생성합니다.
    
    Args:
        question: 생성할 질문 정보
        db: 데이터베이스 세션 (의존성 주입)
        
    Returns:
        생성된 질문 정보를 포함한 응답
    """
    db_question = create_question(db, question)
    return ApiResponse(
        status='success',
        message='질문이 성공적으로 생성되었습니다.',
        data={
            'id': db_question.id,
            'subject': db_question.subject,
            'content': db_question.content,
            'create_date': db_question.create_date.isoformat()
        }
    )


@router.get('/questions', response_model=ApiResponse)
def get_questions_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    질문 목록을 조회합니다.
    
    Args:
        skip: 건너뛸 레코드 수
        limit: 최대 조회할 레코드 수
        db: 데이터베이스 세션 (의존성 주입)
        
    Returns:
        질문 목록을 포함한 응답
    """
    questions = get_questions(db, skip=skip, limit=limit)
    return ApiResponse(
        status='success',
        data={
            'questions': [
                {
                    'id': q.id,
                    'subject': q.subject,
                    'content': q.content,
                    'create_date': q.create_date.isoformat()
                }
                for q in questions
            ],
            'count': len(questions)
        }
    )


@router.get('/questions/{question_id}', response_model=ApiResponse)
def get_question_endpoint(
    question_id: int,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    특정 ID의 질문을 조회합니다.
    
    Args:
        question_id: 조회할 질문의 ID
        db: 데이터베이스 세션 (의존성 주입)
        
    Returns:
        질문 정보를 포함한 응답
        
    Raises:
        HTTPException: 질문을 찾을 수 없는 경우 404 에러
    """
    db_question = get_question(db, question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail='질문을 찾을 수 없습니다.')
    
    return ApiResponse(
        status='success',
        data={
            'id': db_question.id,
            'subject': db_question.subject,
            'content': db_question.content,
            'create_date': db_question.create_date.isoformat()
        }
    )


@router.put('/questions/{question_id}', response_model=ApiResponse)
def update_question_endpoint(
    question_id: int,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    특정 ID의 질문을 수정합니다.
    
    Args:
        question_id: 수정할 질문의 ID
        question_update: 수정할 내용
        db: 데이터베이스 세션 (의존성 주입)
        
    Returns:
        수정된 질문 정보를 포함한 응답
        
    Raises:
        HTTPException: 질문을 찾을 수 없는 경우 404 에러
    """
    db_question = update_question(db, question_id, question_update)
    if db_question is None:
        raise HTTPException(status_code=404, detail='질문을 찾을 수 없습니다.')
    
    return ApiResponse(
        status='success',
        message='질문이 성공적으로 수정되었습니다.',
        data={
            'id': db_question.id,
            'subject': db_question.subject,
            'content': db_question.content,
            'create_date': db_question.create_date.isoformat()
        }
    )


@router.delete('/questions/{question_id}', response_model=ApiResponse)
def delete_question_endpoint(
    question_id: int,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    특정 ID의 질문을 삭제합니다.
    
    Args:
        question_id: 삭제할 질문의 ID
        db: 데이터베이스 세션 (의존성 주입)
        
    Returns:
        삭제 성공 메시지를 포함한 응답
        
    Raises:
        HTTPException: 질문을 찾을 수 없는 경우 404 에러
    """
    success = delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail='질문을 찾을 수 없습니다.')
    
    return ApiResponse(
        status='success',
        message='질문이 성공적으로 삭제되었습니다.'
    )