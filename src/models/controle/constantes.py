from pathlib import Path
from dotenv import load_dotenv
from jinja2 import Template
from langfuse import Langfuse

load_dotenv()
langfuse = Langfuse()

_PROMPTS_DIR = Path(__file__).parent / "prompts"

BASE_URL_COMMAND = "http://localhost:8001/command"
BASE_URL_MOVEMENT = "http://localhost:8001/movement"
BASE_URL_TELEMETRY = "http://localhost:8001/telemetry"

ROTAS_INICIAIS = ["encerrar", "arm_and_takeoff", "go_to_ned", "rtl"]

DESCRICAO_ROTAS = {
    "arm_and_takeoff": "\"arm_and_takeoff\" se o usuário quer armar e decolar o drone, com ou sem altitude especificada",
    "go_to_ned": "\"go_to_ned\" se o usuário quer mover o drone para uma posição NED (norte, leste, baixo)",
    "rtl": "\"rtl\" se o usuário quer pousar e retornar ao ponto de partida",
    "encerrar": "\"encerrar\" se o usuário quer explicitamente finalizar ou encerrar a missão",
}

def montar_system_piloto(situacao: dict) -> str:
    template = Template((_PROMPTS_DIR / "piloto.jinja2").read_text())
    return template.render(
        pos_x=situacao.get("pos_x", 0.0),
        pos_y=situacao.get("pos_y", 0.0),
        pos_z=situacao.get("pos_z", 0.0),
    )

def montar_system_roteamento(rotas_disponiveis: list[str]) -> str:
    template = Template((_PROMPTS_DIR / "roteamento.jinja2").read_text())
    rotas_filtradas = [r for r in rotas_disponiveis if r in DESCRICAO_ROTAS]
    return template.render(
        rotas=rotas_filtradas,
        descricao_rotas=DESCRICAO_ROTAS,
    )
