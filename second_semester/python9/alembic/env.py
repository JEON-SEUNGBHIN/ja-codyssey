from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# 현재 파일 기준으로 프로젝트 루트 추가 (database, models import 위해)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from database import Base, DATABASE_URL  # noqa: E402
import models  # noqa: F401,E402  # 모델을 import 해서 Base에 등록

# 이 아래는 Alembic 기본 템플릿 로직

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ 여기서 Alembic에게 사용할 MetaData를 알려준다
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,  # ✅ 반드시 포함
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
