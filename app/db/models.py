"""
Módulo de modelos do banco de dados.
Define as tabelas da aplicação e seus relacionamentos usando SQLAlchemy.
Cada classe representa uma tabela no banco de dados.
"""
from datetime import datetime

from app.db.enums import TransactionType
from sqlalchemy import Integer, String, Float, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base
from app.core.utils import get_current_time



class User(Base):
    """
    Tabela de usuários da aplicação.
    Armazena as credenciais de acesso. A senha nunca é salva em texto puro,
    apenas seu hash gerado pelo módulo de segurança.    
    """
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    # O email é usado como identificador único do usuário no login.
    # O índice (index=True) acelera as buscas por email no banco de dados.

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    # Armazena apenas o hash da senha, nunca a senha original.

    account: Mapped["Account"] = relationship("Account", back_populates="user", uselist=False)
    # Relacionamento com a conta corrente do usuário.
    # O uselist=False indica que cada usuário possui apenas uma conta.
    # O back_populates cria a referência inversa: account.user retorna o usuário.


class Account(Base):
    """
    Tabela de contas correntes.
    Cada conta pertence a um único usuário e pode ter múltiplas transações.    
    """
    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    # Saldo atual da conta. Começa em zero e é atualizado a cada transação.

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    # Chave estrangeira que vincula a conta ao seu dono.
    # Garante que não exista conta sem um usuário associado no banco.

    user: Mapped["User"] = relationship("User", back_populates="account")
    # Referência inversa ao usuário dono da conta.

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="account", cascade="all, delete")
    # Lista de todas as transações realizadas nessa conta.
    # O cascade="all, delete" garante que se a conta for deletada,
    # todas as suas transações também serão removidas automaticamente.

class Transaction(Base):
    """
    Tabela de transações bancárias.
    Registra cada depósito ou saque realizado em uma conta.
    Funciona como um histórico imutável de todas as movimentações.
    """
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType), nullable=False)
    # Tipo da transação: depósito ou saque.
    # SAEnum garante que apenas valores válidos do TransactionType
    # sejam aceitos pelo banco de dados.

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    # Valor da transação. Sempre positivo — o tipo define se é entrada ou saída.

    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_current_time, nullable=False)
    # Data e hora da transação registrada automaticamente no momento da criação.
    # O timezone.utc garante consistência independente do fuso horário do servidor.

    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("contas.id"), nullable=False)
    # Chave estrangeira que vincula a transação à sua conta.

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
    # Referência à conta onde a transação foi realizada.