from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .estado import Estado
from .nos import receber_comando, tratar_comando, no_arm, no_takeoff, no_go_to_ned, no_update_estado, rotear, no_rtl


def construir_grafo() -> StateGraph:
    workflow = StateGraph(Estado)

    workflow.add_node("receber_comando", receber_comando)
    workflow.add_node("tratar_comando", tratar_comando)
    workflow.add_node("no_arm", no_arm)
    workflow.add_node("no_takeoff", no_takeoff)
    workflow.add_node("no_go_to_ned", no_go_to_ned)
    workflow.add_node("no_rtl", no_rtl)
    workflow.add_node("no_update_estado", no_update_estado)

    workflow.add_edge(START, "receber_comando")
    workflow.add_edge("receber_comando", "tratar_comando")
    workflow.add_conditional_edges("tratar_comando", rotear, {
        "arm": "no_arm",
        "takeoff": "no_takeoff",
        "go_to_ned": "no_go_to_ned",
        "rtl": "no_rtl",
    })
    workflow.add_edge("no_arm", "receber_comando")
    workflow.add_edge("no_takeoff", "no_update_estado")
    workflow.add_edge("no_go_to_ned", "no_update_estado")
    workflow.add_edge("no_update_estado", "receber_comando")
    workflow.add_edge("no_rtl", END)

    return workflow.compile(checkpointer=MemorySaver())
