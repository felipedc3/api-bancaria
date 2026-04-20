"""
Módulo de endpoints de transações bancárias.
Gerencia depósitos, saques e exibição do extrato da conta,
garantindo que todas as operações sejam validadas antes de
serem persistidas no banco de dados.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models import User, Account, Transaction
from app.db.enums import TransactionType
from app.schemas.transaction import CreateTransaction, TransactionResponse, CreateTransfer
from app.core.security import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transações"])
# O prefix "/transactions" agrupa todos os endpoints de transações.
# As tags organizam os endpoints na documentação do Swagger.

async def get_account_or_404(user: User, db: AsyncSession) -> Account:
    """
    Função auxiliar que busca a conta do usuário autenticado.
    Centraliza a busca da conta em um único lugar para evitar
    repetição de código nos endpoints de depósito, saque e extrato.
    Lança um erro 404 automaticamente se a conta não for encontrada.
    """
    result = await db.execute(select(Account).where(Account.user_id == user.id))
    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada."
        )
    
    return account

@router.post("/deposit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def deposit(
    transaction_data: CreateTransaction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Realiza um depósito na conta do usuário autenticado.
    O valor é validado pelo schema CreateTransaction antes de chegar aqui,
    garantindo que apenas valores positivos sejam aceitos.
    O saldo da conta é atualizado e a transação é registrada no banco.
    """

    account = await get_account_or_404(current_user, db)

    # Atualiza o saldo da conta somando o valor depositado.
    account.balance += transaction_data.amount

    # Registra a transação como depósito no histórico da conta.
    new_transaction = Transaction(
        type = TransactionType.deposito,
        amount = transaction_data.amount,
        account_id = account.id
    )
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    return new_transaction

@router.post("/withdraw", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def withdraw(
    transaction_data: CreateTransaction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Realiza um saque na conta do usuário autenticado.
    Valida se o saldo disponível é suficiente antes de processar o saque,
    bloqueando a operação com erro 400 se não houver saldo suficiente.
    O saldo da conta é atualizado e a transação é registrada no banco.
    """

    account = await get_account_or_404(current_user, db)

    # Valida se o saldo é suficiente antes de processar o saque.
    # Essa validação é feita aqui pois depende do saldo atual da conta,
    # que só temos acesso após buscar a conta no banco.
    if account.balance < transaction_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente."
        )

    # Atualiza o saldo da conta subtraindo o valor sacado.
    account.balance -= transaction_data.amount

    # Registra a transação como saque no histórico da conta.
    new_transaction = Transaction(
        type=TransactionType.saque,
        amount=transaction_data.amount,
        account_id=account.id
    )
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    return new_transaction

@router.get("/statement", response_model=list[TransactionResponse], status_code=status.HTTP_200_OK)
async def get_statement(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o extrato completo da conta do usuário autenticado.
    Lista todas as transações em ordem cronológica decrescente,
    ou seja, as transações mais recentes aparecem primeiro,
    seguindo o padrão dos extratos bancários tradicionais.
    """
    account = await get_account_or_404(current_user, db)

    # Busca todas as transações da conta ordenadas pela data de criação.
    # O order_by com desc() garante que as mais recentes apareçam primeiro.
    result = await db.execute(
        select(Transaction).where(Transaction.account_id == account.id).order_by(Transaction.created_at.desc())
    )
    transactions = result.scalars().all()

    return transactions


@router.post("/transfer", response_model=list[TransactionResponse], status_code=status.HTTP_201_CREATED)
async def transfer(
    transaction_data: CreateTransfer,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Realiza uma transferência entre duas contas.
    Valida se a conta de destino existe e se o saldo da conta de origem
    é suficiente antes de processar a transferência.
    As duas transações — débito na origem e crédito no destino — são
    salvas atomicamente, ou seja, se uma falhar, nenhuma é persistida,
    garantindo que o dinheiro nunca seja perdido ou duplicado.
    Retorna as duas transações geradas: o débito e o crédito.
    """

    # Busca a conta de origem do usuário autenticado.
    source_account = await get_account_or_404(current_user, db)

    # Garante que o usuário não está transferindo para a própria conta.
    if source_account.id == transaction_data.target_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível transferir para a própria conta."
        )
    
    # Busca a conta de destino pelo id informado.
    result = await db.execute(
        select(Account).where(Account.id == transaction_data.target_account_id)
    )
    target_account = result.scalar_one_or_none()


    # Valida se a conta de origem tem saldo suficiente.
    if target_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta de destino não encontrada."
        )
    

    # Debita o valor da conta de origem.
    source_account.balance = source_account.balance - transaction_data.amount

    # Credita o valor na conta de destino.
    target_account.balance = target_account.balance + transaction_data.amount

    # Registra a transação de débito na conta de origem.
    debit_transaction = Transaction(
        type=TransactionType.transferencia,
        amount=transaction_data.amount,
        account_id=source_account.id
    )

    # Registra a transação de crédito na conta de destino.
    credit_transaction = Transaction(
        type=TransactionType.transferencia,
        amount=transaction_data.amount,
        account_id=target_account.id
    )

    db.add(debit_transaction)
    db.add(credit_transaction)

    # O commit salva todas as operações atomicamente.
    # Se qualquer operação falhar, o banco reverte tudo automaticamente.
    await db.commit()
    await db.refresh(debit_transaction)
    await db.refresh(credit_transaction)

    return [debit_transaction, credit_transaction]
