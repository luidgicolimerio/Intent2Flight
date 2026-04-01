from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .estado import Estado
from .nos import receber_comando, tratar_comando, executa_comando, busca_situacao, rotear


def construir_grafo() -> StateGraph:
    workflow = StateGraph(Estado)

    workflow.add_node("receber_comando", receber_comando)
    workflow.add_node("tratar_comando", tratar_comando)
    workflow.add_node("executa_comando", executa_comando)
    workflow.add_node("busca_situacao", busca_situacao)

    workflow.add_edge(START, "receber_comando")
    workflow.add_edge("receber_comando", "busca_situacao")
    workflow.add_edge("busca_situacao", "tratar_comando")
    workflow.add_conditional_edges("tratar_comando", rotear, {
        "executa_comando": "executa_comando",
        "END": END,
    })
    workflow.add_edge("executa_comando", "receber_comando")

    return workflow.compile(checkpointer=MemorySaver())
