"""
Módulo de schemas de conta corrente.
Define os formatos de saída dos dados da conta, incluindo
o saldo atual e as informações do titular.
"""

from pydantic import BaseModel

class AccountResponse(BaseModel):
    """
    Schema de saída para retorno dos dados da conta corrente.
    Exibe o saldo atual da conta vinculada ao usuário autenticado.
    O from_attributes permite que o Pydantic leia os dados diretamente
    de um objeto do SQLAlchemy, sem precisar converter manualmente para dicionário.
    """

    id: int 
    balance: float

    model_config = {"from_attributes": True}