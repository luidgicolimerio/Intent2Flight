from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_URL_COMMAND = "http://localhost:8001/command"
BASE_URL_MOVEMENT = "http://localhost:8001/movement"
BASE_URL_TELEMETRY = "http://localhost:8001/telemetry"
MCP_URL = "http://localhost:8001/mcp"

ROTAS_INICIAIS = ["arm", "takeoff", "go_to_ned", "rtl"]

DESCRICAO_ROTAS = {
    "arm": "\"arm\" se o usuário quer armar o drone",
    "takeoff": "\"takeoff\" se o usuário quer decolar, com ou sem altitude especificada",
    "go_to_ned": "\"go_to_ned\" se o usuário quer mover o drone para uma posição NED (norte, leste, baixo)",
    "rtl": "\"rtl\" se o usuário quer encerrar, pousar o drone e retornar ao ponto de partida",
}

_jinja = Environment(loader=FileSystemLoader(Path(__file__).parent / "prompts"), trim_blocks=True, lstrip_blocks=True)


def montar_system_piloto(situacao: dict) -> str:
    return _jinja.get_template("piloto.jinja2").render(
        pos_x=situacao.get("pos_x", 0.0),
        pos_y=situacao.get("pos_y", 0.0),
        pos_z=situacao.get("pos_z", 0.0),
    )


def montar_system_roteamento(rotas_disponiveis: list[str]) -> str:
    return _jinja.get_template("roteamento.jinja2").render(
        rotas=[r for r in rotas_disponiveis if r in DESCRICAO_ROTAS],
        descricao_rotas=DESCRICAO_ROTAS,
    )
