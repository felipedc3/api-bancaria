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

async def create_second_user(client: AsyncClient) -> int:
    """
    Função auxiliar que cadastra um segundo usuário e retorna o id da sua conta.
    Usada nos testes de transferência para simular uma conta de destino.
    """
    await client.post("/auth/register", json={
        "name": "João",
        "email": "joao@email.com",
        "password": "123456"
    })

    response = await client.post("/auth/login", json={
        "email": "joao@email.com",
        "password": "123456"
    })

    token = response.json()["access_token"]

    response = await client.get(
        "/accounts/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    return response.json()["id"]

@pytest.mark.asyncio
async def test_transfer_success(client: AsyncClient):
    """
    Testa uma transferência com saldo suficiente.
    Verifica se o endpoint retorna status 201 e as duas transações geradas,
    confirmando que o débito e o crédito foram registrados corretamente.
    """
    token = await create_and_login(client)
    target_account_id = await create_second_user(client)

    await client.post(
        "/transactions/deposit",
        json={"amount": 500.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.post(
        "/transactions/transfer",
        json={"target_account_id": target_account_id, "amount": 200.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[0]["type"] == "transferencia"
    assert data[1]["type"] == "transferencia"
    assert data[0]["amount"] == 200.00
    assert data[1]["amount"] == 200.00

@pytest.mark.asyncio
async def test_transfer_insufficient_balance(client: AsyncClient):
    """
    Testa uma transferência com saldo insuficiente.
    Verifica se o endpoint retorna status 400 e a mensagem de erro correta,
    impedindo que o saldo fique negativo.
    """
    token = await create_and_login(client)
    target_account_id = await create_second_user(client)

    response = await client.post(
        "/transactions/transfer",
        json={"target_account_id": target_account_id, "amount": 500.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_transfer_to_same_account(client: AsyncClient):
    """
    Testa uma transferência para a própria conta.
    Verifica se o endpoint retorna status 400 e a mensagem de erro correta,
    impedindo que o usuário transfira para si mesmo.
    """

    token = await create_and_login(client)

    response = await client.get(
        "/accounts/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    own_account_id = response.json()["id"]

    response = await client.post(
        "/transactions/transfer",
        json={"target_account_id": own_account_id, "amount": 100.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Não é possível transferir para a própria conta."

@pytest.mark.asyncio
async def test_transfer_to_noexistent_account(client: AsyncClient):
    """
    Testa uma transferência para uma conta inexistente.
    Verifica se o endpoint retorna status 404 e a mensagem de erro correta,
    impedindo transferências para contas que não existem.
    """
    token = await create_and_login(client)

    await client.post(
        "/transactions/deposit",
        json={"amount": 500.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.post(
        "/transactions/transfer",
        json={"target_account_id": 9999, "amount": 100.00},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Conta de destino não encontrada."

