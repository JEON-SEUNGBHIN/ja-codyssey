from typing import Optional

from pydantic import BaseModel


class Todo(BaseModel):
    id: int
    title: str
    description: str = ''
    is_done: bool = False


class Todoltem(BaseModel):
    """수정 및 생성에 사용하는 모델 (id 는 경로 매개변수 사용)"""

    title: str
    description: str = ''
    is_done: bool = False
