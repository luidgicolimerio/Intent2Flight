from ..estado import EstadoMissao
from ..agentes import agente_operador
from src.models.controle.grafo import construir_grafo as construir_grafo_controle

_grafo_controle = construir_grafo_controle()


async def operador(state: EstadoMissao) -> dict:
    fila = state["plano_de_voo"]
    if not fila:
        return {"status_missao": "concluido", "comando_ativo": None}

    comando_ativo = fila[0]
    instrucao = await agente_operador(comando_ativo)
    try:
        await _grafo_controle.ainvoke({"comando": instrucao})
        return {"plano_de_voo": fila[1:], "comando_ativo": None}
    except Exception as e:
        print(f"[operador] Erro ao executar comando: {e}")
        return {"status_missao": "falha", "comando_ativo": comando_ativo}


def rotear_operador(state: EstadoMissao) -> str:
    status = state["status_missao"]
    if status == "concluido":
        return "END"
    if status == "falha":
        return "planejador"
    return "operador"
