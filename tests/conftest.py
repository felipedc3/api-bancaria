"""
Configurações compartilhadas entre todos os testes.
Define as fixtures que preparam e limpam o ambiente de teste,
garantindo que cada teste rode de forma isolada e independente.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.db.database import Base, get_db

# URL do banco de dados exclusivo para testes.
# Usamos um banco separado para nunca interferir nos dados reais da aplicação.
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    """
    Fixture que cria e limpa o banco de dados antes e depois de cada teste.
    O autouse=True garante que ela rode automaticamente em todos os testes
    sem precisar ser declarada explicitamente em cada um.
    Criar as tabelas antes e apagá-las depois garante que cada teste
    começa com um banco completamente limpo e isolado.
    """

@pytest_asyncio.fixture
async def client():
    """
    Fixture que fornece um cliente HTTP assíncrono para os testes.
    O AsyncClient simula requisições HTTP reais para a API sem precisar
    subir um servidor, tornando os testes mais rápidos e confiáveis.
    O override de get_db garante que os testes usem o banco de testes
    em vez do banco real da aplicação.
    """

    async def override_get_db():
        """
        Substitui a dependência get_db pelo banco de testes.
        Isso garante que todas as operações durante os testes
        sejam feitas no banco isolado, nunca no banco real.
        """
        
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()