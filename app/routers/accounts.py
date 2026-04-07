"""
Módulo de endpoints de contas correntes.
Gerencia a exibição dos dados da conta do usuário autenticado,
protegido por autenticação JWT para garantir que cada usuário
acesse apenas os dados da sua própria conta.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models import User, Account
from app.schemas.account import AccountResponse
from app.core.security import get_current_user

# O prefix "/accounts" agrupa todos os endpoints relacionados a contas.
# As tags organizam os endpoints na documentação do Swagger.
router = APIRouter(prefix="/accounts", tags=["Contas"])

@router.get("/me", response_model=AccountResponse, status_code=status.HTTP_200_OK)
async def get_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna os dados da conta corrente do usuário autenticado.
    O Depends(get_current_user) garante que apenas usuários com token
    JWT válido consigam acessar esse endpoint, bloqueando automaticamente
    qualquer requisição sem autenticação válida.
    """

    result = await db.execute(select(Account).where(Account.user_id == current_user.id))
    account = result.scalar_one_or_none()
    # Busca a conta vinculada ao usuário autenticado.
    # scalar_one_or_none() retorna a conta ou None se não existir.

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    return account