from langchain_core.runnables import RunnableConfig
from ..estado import EstadoMissao
from ..agentes import agente_operador
from src.models.controle.grafo import construir_grafo as construir_grafo_controle
import uuid

_grafo_controle = construir_grafo_controle()

FROTA_MCP_MAP = {
    "drone_1": "http://localhost:8010/mcp",
    "drone_2": "http://localhost:8011/mcp",
    "drone_3": "http://localhost:8012/mcp",
    "drone_4": "http://localhost:8013/mcp",
}

async def operador(state: EstadoMissao, config: RunnableConfig) -> dict:
    fila = state["plano_de_voo"]
    if not fila:
        return {"status_missao": "concluido", "comando_ativo": None}

    comando_ativo = fila[0]

    alvo = comando_ativo.get("alvo", "drone_1")
    url_do_drone = FROTA_MCP_MAP.get(alvo, "http://localhost:8010/mcp")

    instrucao = await agente_operador(comando_ativo)
    print(f"\n[Operador] Enviando para {alvo} ({url_do_drone}): {instrucao}")

    config_filho = {
        "callbacks": config.get("callbacks"),
        "configurable": {"thread_id": str(uuid.uuid4())}
    }

    try:
        await _grafo_controle.ainvoke({"comando": instrucao, "mcp_url": url_do_drone}, config=config_filho)
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
