import asyncio
import os
import sys
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Adicione o diretório do projeto ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.makedirs(os.path.join(os.path.dirname(__file__), "versions"), exist_ok=True)

# Importe os modelos
from app.models.base import Base
from app.core.config import settings

config = context.config
fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

connectable = AsyncEngine(
    engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
)

async def run_migrations_online():
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        async with connection.begin():
            await connection.run_sync(lambda sync_conn: context.run_migrations())

if context.is_offline_mode():
    raise NotImplementedError("Offline mode not supported")
else:
    asyncio.run(run_migrations_online())