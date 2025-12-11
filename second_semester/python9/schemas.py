"""
Pydantic 스키마 모델 정의

API 요청/응답에 사용되는 데이터 모델을 정의합니다.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    """질문 생성 요청 모델

    제목과 내용은 빈 문자열을 허용하지 않는다.
    """
    subject: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class QuestionUpdate(BaseModel):
    """질문 수정 요청 모델"""
    subject: Optional[str] = None
    content: Optional[str] = None


class QuestionResponse(BaseModel):
    """질문 응답 모델"""
    id: int
    subject: str
    content: str
    create_date: datetime

    class Config:
        # SQLAlchemy ORM 객체를 그대로 넣어도 변환될 수 있도록 설정
        from_attributes = True


class QuestionListResponse(BaseModel):
    """질문 목록 응답 모델"""
    questions: list[QuestionResponse]
    count: int


class ApiResponse(BaseModel):
    """
    API 공통 응답 모델

    status: 'success' | 'error' 등의 상태 문자열
    message: 선택적인 설명 메시지
    data: 실제 응답 데이터(예: {'questions': [...], 'count': 10})
    """
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
