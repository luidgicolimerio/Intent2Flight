from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .estado import EstadoMissao
from .nos import entrada_humana, planejador, auditor, rotear_auditor, operador, rotear_operador


def construir_grafo() -> StateGraph:
    workflow = StateGraph(EstadoMissao)

    workflow.add_node("entrada_humana", entrada_humana)
    workflow.add_node("planejador", planejador)
    workflow.add_node("auditor", auditor)
    workflow.add_node("operador", operador)

    workflow.add_edge(START, "entrada_humana")
    workflow.add_edge("entrada_humana", "planejador")
    workflow.add_edge("planejador", "auditor")

    workflow.add_conditional_edges("auditor", rotear_auditor, {
        "planejador": "planejador",
        "operador": "operador",
    })

    workflow.add_conditional_edges("operador", rotear_operador, {
        "operador": "operador",     # Ainda há comandos na fila, continua iterando
        "planejador": "planejador",
        "END": END,
    })

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory, interrupt_before=["operador"])
