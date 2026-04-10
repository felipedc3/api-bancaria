"""
Módulo de segurança da aplicação.
Responsável por duas funções essenciais de segurança:
1. Hash de senhas: garante que senhas nunca sejam salvas em texto puro no banco.
2. Geração e validação de tokens JWT: controla o acesso autenticado à API.
"""

from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.database import get_db


"""
Contexto de criptografia configurado com o algoritmo bcrypt.
O bcrypt é o algoritmo recomendado para hash de senhas pois, ao contrário
de algoritmos como MD5 ou SHA-1, ele foi projetado especificamente para
ser lento, dificultando ataques de força bruta mesmo se o banco for invadido.
O parâmetro "deprecated=auto" garante que hashes antigos sejam atualizados
automaticamente caso o algoritmo seja trocado no futuro.
"""

def hash_password(password: str) -> str:
    """
    Transforma uma senha pura em um hash seguro usando bcrypt.
    Nunca salvamos a senha original no banco de dados, apenas seu hash.
    Assim, mesmo que o banco seja comprometido, as senhas dos usuários
    permanecem protegidas pois o hash é irreversível
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hased_password: str) -> bool:
    """
    Verifica se a senha digitada no login corresponde ao hash salvo no banco.
    Não descriptografa o hash — aplica o mesmo processo na senha digitada
    e compara os resultados. Retorna True se a senha estiver correta,
    False caso contrário.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hased_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """
    Gera um token JWT assinado com as informações do usuário autenticado.
    O token carrega os dados do usuário (como o email) e uma data de expiração.
    Ele é assinado com a SECRET_KEY, o que garante que qualquer adulteração
    no token seja detectada na próxima validação, bloqueando o acesso.
    """

    to_encode = data.copy()
    # Fazemos uma cópia para não modificar o dicionário original recebido.
    
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Calcula o momento exato em que o token deixará de ser válido.
    # Usar UTC garante consistência independente do fuso horário do servidor.
    
    to_encode.update({"exp": expire})
    # Adiciona a expiração ao payload do token antes de assinar.
    # O campo "exp" é um padrão do JWT e é verificado automaticamente
    # pelo python-jose na hora de decodificar o token.
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    """
    Decodifica e valida um token JWT recebido em uma requisição.
    Verifica automaticamente se a assinatura é válida e se o token
    não expirou. Retorna os dados contidos no token se for válido,
    ou None se o token for inválido, adulterado ou expirado,
    evitando que a exceção quebre o fluxo da aplicação.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except JWTError:
        return None
    
oauth2_scheme = HTTPBearer()
# Define o endpoint onde o token será obtido.
# O OAuth2PasswordBearer instrui o Swagger a exibir o botão "Authorize",
# permitindo testar os endpoints protegidos diretamente na documentação.

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Extrai o token das credenciais recebidas no cabeçalho Authorization.
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception

    from app.db.models import User
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user
