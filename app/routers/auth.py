"""
Módulo de autenticação da aplicação.
Gerencia o cadastro de novos usuários e o login, sendo responsável
por gerar os tokens JWT que protegem os demais endpoints da API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models import User, Account
from app.schemas.user import CreateUser, UserResponse, LoginUser
from app.core.security import hash_password, verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Autenticação"])
# O APIRouter agrupa os endpoints relacionados à autenticação.
# O prefix define que todas as rotas desse router começam com /auth.
# As tags organizam os endpoints na documentação do Swagger.

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: CreateUser, db: AsyncSession = Depends(get_db)):
    """
    Cadastra um novo usuário e cria automaticamente sua conta corrente.
    Verifica se o email já está cadastrado antes de criar o usuário,
    garantindo que não existam dois usuários com o mesmo email.
    A senha é transformada em hash antes de ser salva no banco,
    garantindo que nunca seja armazenada em texto puro.
    """

    # Verifica se já existe um usuário com esse email no banco.
    result = await db.execute(select(User).where(User.email == user_data.email))
    
    # scalar_one_or_none() retorna o usuário encontrado ou None caso não exista.
    # É mais seguro que scalar_one() pois não lança exceção quando não há resultado.
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado."
        )
    

    # Cria o usuário com a senha transformada em hash.
    new_user = User(
        name = user_data.name,
        email = user_data.email,
        hashed_password = hash_password(user_data.password)
    )
    db.add(new_user)
    
    await db.flush()
    # Cria automaticamente uma conta corrente para o novo usuário.
    # O flush() acima garante que o new_user já tem um id gerado
    # pelo banco antes de criar a conta vinculada a ele.

    new_account = Account(user_id = new_user.id)
    db.add(new_account)


    # O commit() confirma todas as operações pendentes no banco de uma vez.
    # O refresh() atualiza o objeto new_user com os dados mais recentes do banco,
    # como o id gerado, necessário para montar a resposta corretamente.    
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: LoginUser, db: AsyncSession = Depends(get_db)):
    """
    Autentica o usuário e retorna um token JWT.
    Verifica se o email existe e se a senha está correta.
    Retorna um token de acesso que deve ser enviado nas
    próximas requisições para acessar endpoints protegidos.
    """

    # Busca o usuário pelo email no banco de dados.
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    # Usamos a mesma mensagem de erro para email e senha inválidos
    # intencionalmente, para não revelar se o email existe ou não no sistema.
    # evitando que atacantes usem o endpoint para descobrir emails cadastrados.
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos."
        )    


    # Gera o token JWT com o email do usuário como identificador.
    # O campo "sub" (subject) é uma convenção do padrão JWT para
    # identificar o dono do token.    
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}