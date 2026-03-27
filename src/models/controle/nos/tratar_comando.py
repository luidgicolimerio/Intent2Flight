import asyncio
from ..estado import Estado
from ..constantes import MCP_URL, montar_system_roteamento
from ..agentes import agente_roteamento


def tratar_comando(estado: Estado) -> dict:
    print(f"[tratar_comando] Analisando comando: '{estado['comando']}'")
    rotas = estado["situacao"]["rotas_disponiveis"]
    rota = asyncio.run(agente_roteamento(
        MCP_URL,
        montar_system_roteamento(rotas),
        estado["comando"],
    ))
    print(f"[tratar_comando] Rota decidida: '{rota}'")
    return {"rota": rota}


def rotear(estado: Estado) -> str:
    return estado["rota"]
