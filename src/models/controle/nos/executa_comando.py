import asyncio
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools.base import ToolException
from ..estado import Estado
from ..constantes import montar_system_piloto
from ..agentes import agente_piloto


def executa_comando(estado: Estado, config: RunnableConfig) -> dict:
    print(f"[executa_comando] Executando rota: '{estado['rota']}' | comando: '{estado['comando']}'")
    rota = estado["rota"]
    sucesso = True

    url_mcp_dinamica = estado["mcp_url"] 

    try:
        resposta = asyncio.run(agente_piloto(
            url_mcp_dinamica,
            montar_system_piloto(estado["situacao"]),
            rota,
            estado["comando"],
            callbacks=config.get("callbacks"),
        ))
        ultima_msg = resposta["messages"][-1].content
    except (ToolException, Exception) as e:
        print(f"[executa_comando] Erro ao executar comando: {e}")
        ultima_msg = f"Falha ao executar o comando: {e}"
        sucesso = False
    print(f"[executa_comando] Resposta do piloto: {ultima_msg}")
    situacao = dict(estado["situacao"])
    if sucesso:
        if rota == "arm_and_takeoff":
            rotas = [r for r in situacao["rotas_disponiveis"] if r != "arm_and_takeoff"]
            situacao = {**situacao, "no_ar": True, "rotas_disponiveis": rotas}
        elif rota == "rtl":
            rotas = situacao["rotas_disponiveis"]
            if "arm_and_takeoff" not in rotas:
                rotas = ["arm_and_takeoff"] + rotas
            situacao = {**situacao, "no_ar": False, "rotas_disponiveis": rotas}
    return {
        "messages": [AIMessage(content=ultima_msg)],
        "rota": None,
        "situacao": situacao,
    }
