"""
Testes dos endpoints de autenticação.
Verifica o comportamento do registro e login de usuários,
incluindo os casos de sucesso e os casos de erro esperados.
"""

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """
    Testa o cadastro de um novo usuário com sucesso.
    Verifica se o endpoint retorna status 201 e os dados corretos,
    sem expor a senha na resposta.
    """
    response = await client.post("/auth/register", json={
        "name": "Felipe",
        "email": "felipe@email.com",
        "password": "123456"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "felipe@email.com"
    assert data["name"] == "Felipe"
    assert "password" not in data
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """
    Testa o cadastro com um email já existente.
    Verifica se o endpoint retorna status 400 e a mensagem de erro correta,
    impedindo que dois usuários tenham o mesmo email.
    """
    await client.post("/auth/register", json={
        "name": "Felipe",
        "email": "felipe@email.com",
        "password": "123456"
    })


    response = await client.post("/auth/register", json={
        "name": "Felipe",
        "email": "felipe@email.com",
        "password": "123456"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Email já cadastrado."

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """
    Testa o login com credenciais corretas.
    Verifica se o endpoint retorna status 200 e um token JWT válido,
    confirmando que o token é do tipo bearer.
    """
    await client.post("/auth/register", json={
        "name": "Felipe",
        "email": "felipe@email.com",
        "password": "123456"
    })

    response = await client.post("/auth/login", json={
        "email": "felipe@email.com",
        "password": "123456"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """
    Testa o login com senha incorreta.
    Verifica se o endpoint retorna status 401 e a mensagem de erro correta,
    sem revelar se o email existe ou não no sistema.
    """
    await client.post("/auth/register", json={
        "name": "Felipe",
        "email": "felipe@email.com",
        "password": "123456"
    })

    response = await client.post("/auth/login", json={
        "email": "felipe@email.com",
        "password": "senha_errada"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha inválidos."

pytest.mark.asyncio
async def test_login_wrong_email(client: AsyncClient):
    """
    Testa o login com email não cadastrado.
    Verifica se o endpoint retorna a mesma mensagem de erro que senha incorreta,
    evitando que atacantes descubram quais emails estão cadastrados.
    """
    response = await client.post("/auth/login", json={
        "email": "emailnaoexiste@email.com",
        "password": "123456"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha inválidos."