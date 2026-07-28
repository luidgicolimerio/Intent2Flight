import asyncio
import json
from langchain_core.runnables import RunnableConfig
from ..estado import Estado
from ..agentes import agente_telemetria


def busca_situacao(estado: Estado, config: RunnableConfig) -> dict:
    print("[busca_situacao] Buscando telemetria NED...")

    url_mcp_dinamica = estado["mcp_url"] 

    try:
        resposta = asyncio.run(agente_telemetria(url_mcp_dinamica, callbacks=config.get("callbacks")))
        from ..constantes import ROTAS_INICIAIS
        situacao_atual = estado.get("situacao") or {}
        for msg in resposta["messages"]:
            content = getattr(msg, "content", "")
            if not isinstance(content, list):
                continue
            for item in content:
                if item.get("type") != "text":
                    continue
                try:
                    dados = json.loads(item["text"])
                    pos = dados.get("info", {}).get("position", {})
                    vel = dados.get("info", {}).get("velocity", {})
                    if not pos:
                        continue
                    print(f"[busca_situacao] Posição: x={pos.get('x')}, y={pos.get('y')}, z={pos.get('z')}")
                    return {
                        "situacao": {
                            "rotas_disponiveis": situacao_atual.get("rotas_disponiveis", ROTAS_INICIAIS),
                            "no_ar": situacao_atual.get("no_ar", False),
                            "pos_x": pos.get("x", situacao_atual.get("pos_x", 0.0)),
                            "pos_y": pos.get("y", situacao_atual.get("pos_y", 0.0)),
                            "pos_z": pos.get("z", situacao_atual.get("pos_z", 0.0)),
                            "vel_x": vel.get("vx", situacao_atual.get("vel_x", 0.0)),
                            "vel_y": vel.get("vy", situacao_atual.get("vel_y", 0.0)),
                            "vel_z": vel.get("vz", situacao_atual.get("vel_z", 0.0)),
                        }
                    }
                except (json.JSONDecodeError, KeyError):
                    continue
    except Exception as e:
        print(f"[busca_situacao] Erro ao buscar telemetria: {e}")
    return {"situacao": estado["situacao"]}
