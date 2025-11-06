from __future__ import annotations

from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List, Any

import json
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

todo_list: List[Dict[str, Any]] = []
_DATA_DIR = Path('data')
_CSV_PATH = _DATA_DIR / 'todos.csv'
_LOCK = Lock()

def _ensure_storage() -> None:
    if not _DATA_DIR.exists():
        _DATA_DIR.mkdir(parents=True)
    if not _CSV_PATH.exists():
        _CSV_PATH.write_text('ts,item\n', encoding='utf-8')


def _load_from_csv() -> List[Dict[str, Any]]:
    _ensure_storage()
    loaded: List[Dict[str, Any]] = []
    with _CSV_PATH.open('r', encoding='utf-8') as f:
        header = f.readline()
        _ = header
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            try:
                _, json_str = line.split(',', 1)
                obj = json.loads(json_str)
                if isinstance(obj, dict):
                    loaded.append(obj)
            except Exception:
                continue
    return loaded


def _append_to_csv(item: Dict[str, Any]) -> None:
    _ensure_storage()
    ts = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    json_str = json.dumps(item, ensure_ascii=False)
    with _CSV_PATH.open('a', encoding='utf-8', newline='') as f:
        f.write(f'{ts},{json_str}\n')

app = FastAPI(title='Todo API', version='1.0.0')
router = APIRouter()


@router.post('/todo')
def add_todo(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict) or len(payload) == 0:
        return {'ok': False, 'warning': '빈 객체입니다. 최소 1개 이상의 키/값을 제공하세요.'}

    with _LOCK:
        todo_list.append(payload)
        _append_to_csv(payload)

    # 출력도 Dict
    return {
        'ok': True,
        'size': len(todo_list),
        'message': '추가되었습니다.',
    }


@router.get('/todo')
def retrieve_todo() -> Dict[str, Any]:
    with _LOCK:
        return {'todo_list': list(todo_list)}

app.include_router(router)

@app.on_event('startup')
def on_startup() -> None:
    loaded = _load_from_csv()
    with _LOCK:
        todo_list.clear()
        todo_list.extend(loaded)

@app.get('/')
def health() -> Dict[str, str]:
    return {'status': 'ok'}
