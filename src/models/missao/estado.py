from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class ComandoMissao(TypedDict):
    """Estrutura individual de uma tarefa dentro do plano de voo macro"""
    acao: str
    alvo: str | None       
    parametros: dict | None 


class SituacaoFrota(TypedDict):
    """Rastreia o status de alto nível dos 4 drones físicos disponíveis"""
    drone_1: str
    drone_2: str
    drone_3: str
    drone_4: str


class EstadoMissao(TypedDict):
    """Estado principal do Grafo Macro de Missão"""
    
    # Histórico de mensagens para o LLM (Planejador/Auditor) processar o raciocínio
    messages: Annotated[list, add_messages]
    
    # O pedido em linguagem natural feito pelo humano
    objetivo_abstrato: str | None
    
    # A fila de comandos gerada pelo agente planejador
    plano_de_voo: list[ComandoMissao]
    
    # O comando que o operador tirou da fila e enviou para o controle
    comando_ativo: ComandoMissao | None
    
    # Visão macro da frota
    situacao_frota: SituacaoFrota
    
    # Máquina de estados do grafo macro (ex: "planejando", "executando", "falha")
    status_missao: str | None
    
    # Feedback caso o auditor de segurança rejeite o plano
    feedback_auditor: str | None