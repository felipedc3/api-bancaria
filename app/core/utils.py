"""
Módulo de funções utilitárias da aplicação.
Centraliza funções auxiliares reutilizáveis em diferentes partes do sistema,
evitando duplicação de código e facilitando a manutenção.
"""

from datetime import datetime, timezone




def get_current_time() -> datetime:
    """
    Retorna o momento atual com fuso horário UTC explícito.
    Usamos timezone.utc em vez do datetime.utcnow() que está depreciado pois ele
    retorna um datetime 'ingênuo' (sem informação de fuso horário), o que
    pode causar inconsistências ao comparar datas em servidores com fusos
    diferentes. Com timezone.utc, a data sempre carrega a informação do
    fuso horário, tornando as comparações seguras e previsíveis.
    """
    return datetime.now(timezone.utc)