from ..estado import EstadoMissao
from ..agentes import agente_planejador


async def planejador(state: EstadoMissao) -> dict:
    plano = await agente_planejador(
        objetivo_abstrato=state["objetivo_abstrato"],
        situacao_frota=state["situacao_frota"],
        feedback_auditor=state.get("feedback_auditor"),
    )
    return {"plano_de_voo": plano, "status_missao": "auditando"}
