import asyncio
from langchain_core.messages import AIMessage
from ..estado import Estado
from ..constantes import MCP_URL, montar_system_piloto
from ..agentes import agente_piloto


def executa_comando(estado: Estado) -> dict:
    print(f"[executa_comando] Executando rota: '{estado['rota']}' | comando: '{estado['comando']}'")
    resposta = asyncio.run(agente_piloto(
        MCP_URL,
        montar_system_piloto(estado["situacao"]),
        estado["comando"],
    ))
    ultima_msg = resposta["messages"][-1].content
    situacao = _extrair_situacao(resposta, estado["situacao"])
    print(f"[executa_comando] Resposta do piloto: {ultima_msg}")
    return {
        "messages": [AIMessage(content=ultima_msg)],
        "rota": None,
        "situacao": situacao,
    }


def _extrair_situacao(resposta: dict, situacao_atual: dict) -> dict:
    for msg in reversed(resposta["messages"]):
        content = getattr(msg, "content", "")
        if isinstance(content, str) and "position" in content:
            import json, re
            match = re.search(r'\{.*"position".*\}', content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    pos = data.get("position", {})
                    vel = data.get("velocity", {})
                    return {
                        **situacao_atual,
                        "pos_x": pos.get("x", situacao_atual.get("pos_x", 0.0)),
                        "pos_y": pos.get("y", situacao_atual.get("pos_y", 0.0)),
                        "pos_z": pos.get("z", situacao_atual.get("pos_z", 0.0)),
                        "vel_x": vel.get("vx", situacao_atual.get("vel_x", 0.0)),
                        "vel_y": vel.get("vy", situacao_atual.get("vel_y", 0.0)),
                        "vel_z": vel.get("vz", situacao_atual.get("vel_z", 0.0)),
                    }
                except (json.JSONDecodeError, AttributeError):
                    pass
    return situacao_atual
