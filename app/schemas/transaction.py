"""
Módulo de schemas de transações bancárias.
Define os formatos de entrada para criação de transações
e de saída para exibição do extrato bancário.
"""

from datetime import datetime
from pydantic import BaseModel, field_validator
from app.db.enums import TransactionType

class CreateTransaction(BaseModel):
    """
    Schema de entrada para criação de uma nova transação.
    Recebe apenas o valor pois o tipo da transação (depósito ou saque)
    é determinado pelo endpoint acessado, não pelo usuário.
    O field_validator garante que valores negativos ou zerados sejam
    rejeitados antes mesmo de chegar na lógica da aplicação.
    """

    amount: float

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: float) -> float:
        """
        Valida que o valor da transação seja positivo.
        Rejeitar valores negativos ou zero aqui, na entrada dos dados,
        é mais seguro e eficiente do que validar dentro do endpoint,
        pois a requisição é barrada antes de qualquer processamento.
        """

        if value <= 0:
            raise ValueError("O valor da transação deve ser maior que zero.")
        return value
    

class TransactionResponse(BaseModel):
    """
    Schema de saída para retorno dos dados de uma transação.
    Usado tanto na confirmação de um depósito ou saque
    quanto na exibição do extrato completo da conta.
    """

    id: int
    type: TransactionType
    amount: float
    created_at: datetime
    account_id: int

    model_config = {"from_attributes": True}