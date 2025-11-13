from typing import List
from pathlib import Path
import csv

from fastapi import FastAPI, HTTPException

from model import Todo, Todoltem

app = FastAPI()

DATA_FILE = Path('todo.csv')


def read_todos() -> List[Todo]:
    """CSV 파일에서 Todo 목록을 읽어 온다."""
    todos: List[Todo] = []

    if not DATA_FILE.exists():
        return todos

    with DATA_FILE.open(mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            todo = Todo(
                id=int(row['id']),
                title=row['title'],
                description=row.get('description', ''),
                is_done=row.get('is_done', 'False') == 'True',
            )
            todos.append(todo)

    return todos


def write_todos(todos: List[Todo]) -> None:
    """Todo 목록을 CSV 파일에 저장한다."""
    with DATA_FILE.open(mode='w', newline='') as file:
        fieldnames = ['id', 'title', 'description', 'is_done']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for todo in todos:
            writer.writerow(
                {
                    'id': todo.id,
                    'title': todo.title,
                    'description': todo.description,
                    'is_done': str(todo.is_done),
                }
            )


def get_next_id(todos: List[Todo]) -> int:
    """새로운 Todo 에 사용할 다음 id 값을 계산한다."""
    if not todos:
        return 1

    return max(todo.id for todo in todos) + 1


@app.get('/todos', response_model=List[Todo])
def list_todos() -> List[Todo]:
    """전체 목록 조회"""
    return read_todos()


@app.post('/todos', response_model=Todo, status_code=201)
def create_todo(item: Todoltem) -> Todo:
    """Todo 생성"""
    todos = read_todos()
    new_todo = Todo(
        id=get_next_id(todos),
        title=item.title,
        description=item.description,
        is_done=item.is_done,
    )
    todos.append(new_todo)
    write_todos(todos)
    return new_todo


@app.get('/todos/{todo_id}', response_model=Todo)
def get_single_todo(todo_id: int) -> Todo:
    """개별 조회 기능 (GET)"""
    todos = read_todos()

    for todo in todos:
        if todo.id == todo_id:
            return todo

    raise HTTPException(status_code=404, detail='Todo not found')


@app.put('/todos/{todo_id}', response_model=Todo)
def update_todo(todo_id: int, item: Todoltem) -> Todo:
    """수정 기능 (PUT)"""
    todos = read_todos()

    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            updated = Todo(
                id=todo.id,
                title=item.title,
                description=item.description,
                is_done=item.is_done,
            )
            todos[index] = updated
            write_todos(todos)
            return updated

    raise HTTPException(status_code=404, detail='Todo not found')


@app.delete('/todos/{todo_id}', status_code=204)
def delete_single_todo(todo_id: int) -> None:
    """삭제 기능 (DELETE)"""
    todos = read_todos()
    remaining = [todo for todo in todos if todo.id != todo_id]

    if len(remaining) == len(todos):
        raise HTTPException(status_code=404, detail='Todo not found')

    write_todos(remaining)
    # 204 No Content 이므로 별도의 반환 값 없음
    return None
