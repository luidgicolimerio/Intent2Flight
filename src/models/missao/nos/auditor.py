from ..estado import EstadoMissao
from ..agentes import agente_auditor


async def auditor(state: EstadoMissao) -> dict:
    resultado = await agente_auditor(
        plano_de_voo=state["plano_de_voo"],
        situacao_frota=state["situacao_frota"],
    )
    if resultado["status"] == "aprovado":
        return {"status_missao": "executando", "feedback_auditor": None}
    return {"status_missao": "rejeitado", "feedback_auditor": resultado["feedback"]}


def rotear_auditor(state: EstadoMissao) -> str:
    return "operador" if state["status_missao"] == "executando" else "planejador"
