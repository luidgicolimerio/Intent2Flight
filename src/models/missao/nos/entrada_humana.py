from ..estado import EstadoMissao


def entrada_humana(state: EstadoMissao) -> dict:
    objetivo = state["messages"][-1].content
    return {
        "objetivo_abstrato": objetivo,
        "status_missao": "planejando",
        "feedback_auditor": None,
        "plano_de_voo": [],
        "comando_ativo": None,
    }
