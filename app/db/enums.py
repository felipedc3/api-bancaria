"""
Módulo de enumerações do banco de dados.
Centraliza os tipos enumerados usados nos modelos, separando
a definição dos Enums da definição das tabelas para evitar
conflitos de importação e melhorar a organização do código.
"""

import enum


class TransactionType(enum.Enum):
    """
    Enumeração dos tipos de transação possíveis.
    Usar um Enum em vez de strings livres garante que apenas valores
    válidos sejam salvos no banco, evitando inconsistências nos dados.
    """
    deposito = "deposito"
    saque = "saque"