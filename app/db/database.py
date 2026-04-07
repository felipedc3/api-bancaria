"""
Módulo de configuração do banco de dados.
Responsável por criar a conexão assíncrona com o banco, fornecer sessões
para as operações e disponibilizar a classe Base para os modelos de tabela.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=True)
# Cria o engine assíncrono de conexão com o banco de dados.
# O engine é o ponto central de comunicação entre a aplicação e o banco.
# O parâmetro echo=True faz o SQLAlchemy exibir no terminal todos os
# comandos SQL executados, o que facilita muito o debug durante o desenvolvimento.
# IMPORTANTE: Em produção, echo deve ser False para não expor informações sensíveis nos logs.


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
# Fábrica de sessões assíncronas do banco de dados.
# Cada sessão representa uma "conversa" com o banco: abre uma conexão,
# executa as operações e fecha ao terminar, liberando recursos.
# O parâmetro expire_on_commit=False mantém os objetos acessíveis após
# o commit, evitando consultas desnecessárias ao banco para recarregá-los.

Base = declarative_base()
# Classe base que todos os modelos de tabela irão herdar.
# Ao herdar de Base, o SQLAlchemy reconhece a classe como uma tabela
# do banco de dados e gerencia sua criação e mapeamento automaticamente.

async def get_db():
    """
    Função de injeção de dependência do FastAPI para o banco de dados.
    Abre uma sessão, a entrega para o endpoint utilizar e garante que
    ela seja fechada corretamente ao final da requisição, mesmo que
    ocorra algum erro durante o processo. Isso evita vazamento de conexões
    que poderiam sobrecarregar o banco de dados com o tempo.
    """
    async with AsyncSessionLocal() as session:
        yield session