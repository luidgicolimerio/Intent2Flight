import asyncio
from ..estado import Estado
from ..constantes import ROTAS_INICIAIS, montar_system_roteamento
from ..agentes import agente_roteamento


def tratar_comando(estado: Estado) -> dict:
    print(f"[tratar_comando] Analisando comando: '{estado['comando']}'")
    rotas = estado["situacao"]["rotas_disponiveis"]
    resposta = asyncio.run(agente_roteamento(
        montar_system_roteamento(rotas),
        estado["comando"],
    ))
    rota = next((r for r in ROTAS_INICIAIS if r in resposta), rotas[0])
    print(f"[tratar_comando] Rota decidida: '{rota}'")
    return {"rota": rota}


def rotear(estado: Estado) -> str:
    return "END" if estado["rota"] == "encerrar" else "executa_comando"
