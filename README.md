# 🏦 API Bancária Assíncrona com FastAPI

API RESTful assíncrona para gerenciamento de operações bancárias, desenvolvida com FastAPI e SQLAlchemy. O projeto implementa autenticação JWT, operações de depósito e saque, e exibição de extrato bancário.

---

## 🚀 Tecnologias Utilizadas

| Tecnologia | Versão | Descrição |
|---|---|---|
| Python | 3.14 | Linguagem principal |
| FastAPI | latest | Framework web assíncrono |
| SQLAlchemy | latest | ORM para banco de dados |
| SQLite | - | Banco de dados |
| JWT | - | Autenticação via tokens |
| bcrypt | latest | Hash seguro de senhas |
| Pytest | latest | Testes automatizados |
| Poetry | latest | Gerenciamento de dependências |

---

## 📋 Funcionalidades

- ✅ Cadastro de usuários com criação automática de conta corrente
- ✅ Autenticação segura com JWT
- ✅ Depósitos e saques com validação de saldo
- ✅ Extrato bancário em ordem cronológica
- ✅ Validação de valores negativos
- ✅ Proteção de rotas autenticadas
- ✅ Documentação automática com Swagger/OpenAPI
- ✅ Testes automatizados com 100% de cobertura dos endpoints

---

## 🗂️ Estrutura do Projeto

```
api-bancaria/
│
├── app/
│   ├── main.py              ← Ponto de entrada da aplicação
│   │
│   ├── core/
│   │   ├── config.py        ← Configurações centrais
│   │   ├── security.py      ← JWT e autenticação
│   │   └── utils.py         ← Funções utilitárias
│   │
│   ├── db/
│   │   ├── database.py      ← Conexão com o banco de dados
│   │   ├── models.py        ← Modelos das tabelas
│   │   └── enums.py         ← Enumerações
│   │
│   ├── schemas/
│   │   ├── user.py          ← Schemas de usuário
│   │   ├── account.py       ← Schemas de conta
│   │   └── transaction.py   ← Schemas de transação
│   │
│   └── routers/
│       ├── auth.py          ← Endpoints de autenticação
│       ├── accounts.py      ← Endpoints de conta
│       └── transactions.py  ← Endpoints de transações
│
├── tests/
│   ├── conftest.py          ← Configurações dos testes
│   ├── test_auth.py         ← Testes de autenticação
│   └── test_transactions.py ← Testes de transações
│
├── .env                     ← Variáveis de ambiente (não versionado)
├── .gitignore
├── pytest.ini
└── pyproject.toml
```

---

## ⚙️ Como Executar

### Pré-requisitos
- Python 3.12+
- Poetry

### 1 — Clone o repositório
```bash
git clone https://github.com/seu-usuario/api-bancaria.git
cd api-bancaria
```

### 2 — Instale as dependências
```bash
poetry install
```

### 3 — Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite+aiosqlite:///./bank.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> 💡 Para gerar uma SECRET_KEY segura:
> ```bash
> poetry run python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4 — Execute a aplicação
```bash
poetry run uvicorn app.main:app --reload
```

### 5 — Acesse a documentação
```
http://127.0.0.1:8000/docs
```

---

## 🧪 Executando os Testes

```bash
poetry run pytest -v
```

Resultado esperado:
```
12 passed in 13.42s
```

---

## 📡 Endpoints

### 🔐 Autenticação

| Método | Endpoint | Descrição | Autenticação |
|---|---|---|---|
| POST | `/auth/register` | Cadastra novo usuário | ❌ |
| POST | `/auth/login` | Realiza login e retorna token JWT | ❌ |

### 🏦 Contas

| Método | Endpoint | Descrição | Autenticação |
|---|---|---|---|
| GET | `/accounts/me` | Retorna dados da conta do usuário | ✅ |

### 💸 Transações

| Método | Endpoint | Descrição | Autenticação |
|---|---|---|---|
| POST | `/transactions/deposit` | Realiza um depósito | ✅ |
| POST | `/transactions/withdraw` | Realiza um saque | ✅ |
| GET | `/transactions/statement` | Retorna o extrato bancário | ✅ |

---

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação. Para acessar os endpoints protegidos:

1. Cadastre um usuário em `POST /auth/register`
2. Faça login em `POST /auth/login` e copie o `access_token`
3. Envie o token no cabeçalho das requisições:
```
Authorization: Bearer seu-token-aqui
```

---

## 📊 Exemplos de Uso

### Cadastro
```json
POST /auth/register
{
  "name": "Felipe",
  "email": "felipe@email.com",
  "password": "123456"
}
```

### Login
```json
POST /auth/login
{
  "email": "felipe@email.com",
  "password": "123456"
}
```

### Depósito
```json
POST /transactions/deposit
{
  "amount": 1000.00
}
```

### Saque
```json
POST /transactions/withdraw
{
  "amount": 200.00
}
```