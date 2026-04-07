"""
Módulo de schemas de usuário.
Define os formatos de entrada e saída de dados relacionados ao usuário,
garantindo que dados sensíveis como a senha nunca sejam expostos nas respostas.
"""

from pydantic import BaseModel, EmailStr

class CreateUser(BaseModel):
    """
    Schema de entrada para criação de um novo usuário.
    Contém todos os campos obrigatórios para o cadastro.
    O EmailStr valida automaticamente se o email tem formato válido,
    evitando cadastros com emails malformados sem precisar de validação manual.
    """

    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """
    Schema de saída para retorno dos dados do usuário.
    Nunca expõe a senha ou seu hash, apenas as informações seguras.
    O from_attributes permite que o Pydantic leia os dados diretamente
    de um objeto do SQLAlchemy, sem precisar converter manualmente para dicionário.
    """

    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}        