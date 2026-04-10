"""
Ponto de entrada da aplicação.
Responsável por inicializar o FastAPI, registrar os routers
e criar as tabelas no banco de dados na primeira execução.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import engine, Base
from app.routers import auth, accounts, transactions

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    O código antes do 'yield' executa na inicialização do servidor,
    e o código depois do 'yield' executa quando o servidor é encerrado.
    Usamos esse momento para criar as tabelas no banco de dados
    caso ainda não existam, sem apagar dados já existentes.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Cria a instância principal do FastAPI com as informações da API.
# Essas informações aparecem na documentação do Swagger automaticamente.
app = FastAPI(
    title="API Bancária",
    description="API RESTful assíncrona para gerenciamento de operações bancárias.",
    lifespan=lifespan
)


# Registra os routers na aplicação.
# Cada router traz seus próprios endpoints e prefixos definidos anteriormente.
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)