from langgraph.types import interrupt
import requests
import re
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.config import llm
from .estado import Estado, SituacaoDrone
from .constantes import montar_system_extrair_ned, BASE_URL_COMMAND, BASE_URL_MOVEMENT, BASE_URL_TELEMETRY, montar_system_roteamento


def receber_comando(estado: Estado) -> dict:
    print("\n[receber_comando] Aguardando comando...")
    novo_comando = interrupt("Aguardando comando do usuário: ")
    print(f"[receber_comando] Comando recebido: '{novo_comando}'")
    return {"comando": novo_comando, "messages": [HumanMessage(content=novo_comando)]}


def tratar_comando(estado: Estado) -> dict:
    print(f"[tratar_comando] Analisando comando: '{estado['comando']}'")
    rotas = estado["situacao"]["rotas_disponiveis"]
    resposta = llm.invoke([
        SystemMessage(content=montar_system_roteamento(rotas)),
        HumanMessage(content=estado["comando"]),
    ])
    rota = resposta.content.strip().lower()
    print(f"[tratar_comando] Rota decidida: '{rota}'")
    return {"rota": rota}


def no_arm(estado: Estado) -> dict:
    print("[no_arm] Enviando requisição de ARM para a API...")
    response = requests.get(f"{BASE_URL_COMMAND}/arm")
    resultado = response.json()
    print(f"[no_arm] Resposta: {resultado}")
    rotas = [r for r in estado["situacao"]["rotas_disponiveis"] if r != "arm"]
    return {
        "resultado_api": resultado,
        "messages": [AIMessage(content=f"Drone armado: {resultado.get('result')}")],
        "rota": None,
        "situacao": {**estado["situacao"], "rotas_disponiveis": rotas},
    }


def no_update_estado(estado: Estado) -> dict:
    print("[no_update_estado] Buscando telemetria NED...")
    response = requests.get(f"{BASE_URL_TELEMETRY}/ned")
    resultado = response.json()
    print(f"[no_update_estado] Resposta: {resultado}")
    pos = resultado.get("info", {}).get("position", {})
    vel = resultado.get("info", {}).get("velocity", {})
    situacao_atual = estado["situacao"]
    return {
        "resultado_api": resultado,
        "messages": [AIMessage(content=f"Posição atualizada: x={pos.get('x')}, y={pos.get('y')}, z={pos.get('z')}")],
        "rota": None,
        "situacao": {
            **situacao_atual,
            "pos_x": pos.get("x", situacao_atual.get("pos_x", 0.0)),
            "pos_y": pos.get("y", situacao_atual.get("pos_y", 0.0)),
            "pos_z": pos.get("z", situacao_atual.get("pos_z", 0.0)),
            "vel_x": vel.get("vx", situacao_atual.get("vel_x", 0.0)),
            "vel_y": vel.get("vy", situacao_atual.get("vel_y", 0.0)),
            "vel_z": vel.get("vz", situacao_atual.get("vel_z", 0.0)),
        },
    }


def no_takeoff(estado: Estado) -> dict:
    alt = _extrair_altitude(estado["comando"])
    print(f"[no_takeoff] Enviando requisição de TAKEOFF para a API com alt={alt}m...")
    response = requests.get(f"{BASE_URL_COMMAND}/takeoff", params={"alt": alt})
    resultado = response.json()
    print(f"[no_takeoff] Resposta: {resultado}")
    if response.status_code != 200:
        return {
            "resultado_api": resultado,
            "messages": [AIMessage(content=f"Erro na decolagem: {resultado.get('error')}")],
            "rota": None,
        }
    rotas = [r for r in estado["situacao"]["rotas_disponiveis"] if r != "takeoff"]
    return {
        "resultado_api": resultado,
        "messages": [AIMessage(content=f"Decolagem realizada: {resultado.get('result')}")],
        "rota": None,
        "situacao": {**estado["situacao"], "rotas_disponiveis": rotas},
    }


def no_go_to_ned(estado: Estado) -> dict:
    x, y, z = _extrair_ned(estado["comando"], estado["situacao"])
    print(f"[no_go_to_ned] Movendo drone para NED x={x}, y={y}, z={z}...")
    response = requests.post(f"{BASE_URL_MOVEMENT}/go_to_ned", json={"x": x, "y": y, "z": z})
    resultado = response.json()
    print(f"[no_go_to_ned] Resposta: {resultado}")
    return {
        "resultado_api": resultado,
        "messages": [AIMessage(content=f"Movendo para NED: {resultado.get('result')}")],
        "rota": None,
    }


def no_rtl(estado: Estado) -> dict:
    print("[no_rtl] Enviando requisição de RTL para a API...")
    response = requests.get(f"{BASE_URL_COMMAND}/rtl")
    resultado = response.json()
    print(f"[no_rtl] Resposta: {resultado}")
    return {
        "resultado_api": resultado,
        "messages": [AIMessage(content=f"RTL ativado: {resultado.get('result')}")],
        "rota": None,
    }


def rotear(estado: Estado) -> str:
    return estado["rota"]


def _extrair_altitude(comando: str) -> int:
    match = re.search(r"\d+", comando)
    return int(match.group()) if match else 15


def _extrair_ned(comando: str, situacao: dict) -> tuple[float, float, float]:
    resposta = llm.invoke([
        SystemMessage(content=montar_system_extrair_ned(
            situacao.get("pos_x", 0.0),
            situacao.get("pos_y", 0.0),
            situacao.get("pos_z", 0.0),
        )),
        HumanMessage(content=comando),
    ])
    try:
        x, y, z = map(float, resposta.content.strip().split(","))
    except ValueError:
        x, y, z = 0.0, 0.0, 0.0
    return x, y, z
