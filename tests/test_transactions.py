"""
Testes dos endpoints de transações bancárias.
Verifica o comportamento de depósitos, saques e extrato,
incluindo os casos de sucesso e os casos de erro esperados.
"""

import pytest
from httpx import AsyncClient

async def create_and_login(client: AsyncClient) -> str:
    """
    Função auxiliar que cadastra um usuário e retorna o token JWT.
    Evita repetição de código nos testes que precisam de autenticação,
    centralizando o processo de criação de usuário e login em um único lugar.
    """

    await client.post("/auth/register", json={
        "name": "Felipe",
        "email": "felipe@email.com",
        "password": "1234561"
    })

    response = await client.post("/auth/login", json={
        "email": "felipe@email.com",
        "password": "1234561"
    })
    
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_deposit_success(client: AsyncClient):
    """
    Testa um depósito com valor válido.
    Verifica se o endpoint retorna status 201 e os dados corretos
    da transação, confirmando que o tipo é depósito.
    """

    token = await create_and_login(client)


    response = await client.post(
        "/transactions/deposit",
        json={"amount": 500.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "deposito"
    assert data["amount"] == 500.00


@pytest.mark.asyncio
async def test_deposit_negative_amount(client: AsyncClient):
    """
    Testa um depósito com valor negativo.
    Verifica se o endpoint retorna status 422 e bloqueia a operação,
    confirmando que a validação do schema está funcionando corretamente.
    """

    token = await create_and_login(client)

    response = await client.post(
        "/transactions/deposit",
        json={"amount": -100.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_withdraw_success(client: AsyncClient):
    """
    Testa um saque com saldo suficiente.
    Verifica se o endpoint retorna status 201 e os dados corretos
    da transação, confirmando que o tipo é saque.
    """

    token = await create_and_login(client)

    await client.post(
        "/transactions/deposit",
        json={"amount": 500.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.post(
        "/transactions/withdraw",
        json={"amount": 200.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "saque"
    assert data["amount"] == 200.00


@pytest.mark.asyncio
async def test_withdraw_insufficient_balance(client: AsyncClient):
    """
    Testa um saque com saldo insuficiente.
    Verifica se o endpoint retorna status 400 e a mensagem de erro correta,
    impedindo que o saldo fique negativo.
    """

    token = await create_and_login(client)

    response = await client.post(
        "/transactions/withdraw",
        json={"amount": 500.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Saldo insuficiente."


@pytest.mark.asyncio
async def test_statement_success(client: AsyncClient):
    """
    Testa a exibição do extrato com transações realizadas.
    Verifica se o endpoint retorna status 200 e a lista de transações
    na ordem cronológica correta, com o mais recente primeiro.
    """

    token = await create_and_login(client)

    await client.post(
        "/transactions/deposit",
        json={"amount": 500.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    await client.post(
        "/transactions/withdraw",
        json={"amount": 200.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.get(
        "/transactions/statement",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["type"] == "saque"
    assert data[1]["type"] == "deposito"


@pytest.mark.asyncio
async def test_statement_empty(client: AsyncClient):
    """
    Testa a exibição do extrato sem transações.
    Verifica se o endpoint retorna status 200 e uma lista vazia,
    confirmando que a conta foi criada corretamente sem transações.
    """

    token = await create_and_login(client)

    response = await client.get(
        "/transactions/statement",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """
    Testa o acesso sem token JWT.
    Verifica se o endpoint retorna status 403 bloqueando
    qualquer requisição sem autenticação válida.
    """

    response = await client.get("/transactions/statement")

    assert response.status_code == 403