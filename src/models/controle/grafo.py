from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .estado import Estado
from .nos import receber_comando, tratar_comando, executa_comando, rotear


def construir_grafo() -> StateGraph:
    workflow = StateGraph(Estado)

    workflow.add_node("receber_comando", receber_comando)
    workflow.add_node("tratar_comando", tratar_comando)
    workflow.add_node("executa_comando", executa_comando)

    workflow.add_edge(START, "receber_comando")
    workflow.add_edge("receber_comando", "tratar_comando")
    workflow.add_conditional_edges("tratar_comando", rotear, {
        "arm": "executa_comando",
        "takeoff": "executa_comando",
        "go_to_ned": "executa_comando",
        "rtl": "executa_comando",
    })
    workflow.add_edge("executa_comando", "receber_comando")

    return workflow.compile(checkpointer=MemorySaver())
