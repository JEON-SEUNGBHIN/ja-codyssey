"""
Pydantic 스키마 모델 정의

API 요청/응답에 사용되는 데이터 모델을 정의합니다.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class QuestionCreate(BaseModel):
    """질문 생성 요청 모델"""
    subject: str
    content: str


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
        from_attributes = True


class QuestionListResponse(BaseModel):
    """질문 목록 응답 모델"""
    questions: list[QuestionResponse]
    count: int


class ApiResponse(BaseModel):
    """API 공통 응답 모델"""
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None