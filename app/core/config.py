"""
Módulo de configurações centrais da aplicação.
Utiliza pydantic-settings para gerenciar variáveis de ambiente
de forma tipada e segura. evitando erros de configuração em tempo de execução.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Classe que centraliza todas as configurações da aplicação.
    Ter as configurações em um único lugar facilita a manutenção,
    pois qualquer mudança é feita aqui e refletida em toda a aplicação.
    Os valores podem ser sobrescritos por variáveis de ambiente ou por
    um arquivo .env, o que permite usar configurações diferentes para
    desenvolvimento e produção sem alterar o código.
    """

    DATABASE_URL: str = "sqlite+aiosqlite:///./mybank.db"
    """
    URL de conexão com o banco de dados.
    O prefixo "sqlite+aiosqlite://" é necessário para que o SQLAlchemy
    utilize o driver assíncrono (aiosqlite), permitindo que as operações
    de banco de dados não bloqueiem o servidor enquanto aguardam resposta.
    """

    SECRET_KEY: str = "digite-uma-chave-secreta"
    """
    Chave secreta usada para assinar os tokens JWT.
    Essa assinatura garante que o token não foi adulterado pelo cliente.
    Em produção, deve ser uma string longa e aleatória armazenada no .env,
    pois se essa chave vazar, qualquer pessoa pode gerar tokens válidos.
    """

    ALGORITHM: str = "HS256"
    """
    Algoritmo utilizado para assinar o token JWT.
    O HS256 (HMAC com SHA-256) é o padrão mais utilizado no mercado por
    ser seguro e eficiente. Ele garante que apenas quem possui a SECRET_KEY
    consegue gerar ou validar um token, protegendo a API contra acessos falsos.
    """   
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    """
    Tempo de expiração do token JWT em minutos.
    Tokens com vida longa são um risco de segurança: se um token for roubado,
    o invasor terá acesso por mais tempo. 30 minutos é um equilíbrio entre
    segurança e experiência do usuário.
    """


settings = Settings()
"""
Instância global das configurações, importada pelos demais módulos.
Ao instanciar uma única vez aqui, garantimos que toda a aplicação
compartilhe a mesma configuração, evitando inconsistências.
"""