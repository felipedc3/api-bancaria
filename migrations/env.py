"""
Módulo de configuração do ambiente de migrações do Alembic.
Conecta o Alembic aos modelos do SQLAlchemy para detectar
automaticamente as mudanças na estrutura do banco de dados.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from app.db.database import Base
from app.db.models import User, Account, Transaction

# Configuração do logger do Alembic definida no alembic.ini.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Referência aos metadados dos modelos.
# O Alembic usa isso para detectar diferenças entre os modelos
# e o banco de dados atual, gerando as migrações automaticamente.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Executa migrações em modo offline (sem conexão ativa com o banco).
    Útil para gerar scripts SQL para revisar antes de aplicar.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Executa as migrações usando uma conexão ativa com o banco.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Executa migrações em modo online (com conexão ativa com o banco).
    Usa o engine assíncrono para manter consistência com o resto
    da aplicação que também usa operações assíncronas.
    """
    
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise ValueError("A URL do banco de dados não está configurada no alembic.ini.")

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())