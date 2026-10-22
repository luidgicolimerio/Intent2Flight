import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.models.controle.grafo import construir_grafo
from src.utils import langfuse_handler

parser = argparse.ArgumentParser(description="Controle de Drone via LLM")
parser.add_argument("--porta", type=int, default=8010, help="Porta do MCP do drone (padrão: 8010)")
parser.add_argument("--porta-api", type=int, default=8001, help="Porta da UAV API do drone (padrão: 8001)")
args = parser.parse_args()

mcp_url = f"http://localhost:{args.porta}/mcp"
api_url = f"http://localhost:{args.porta_api}"

grafo = construir_grafo()
config = {"callbacks": [langfuse_handler]}

print(f"=== Controle de Drone via LLM | MCP: {mcp_url} | API: {api_url} ===")

estado_base = {
    "messages": [],
    "rota": None,
    "resultado_api": None,
    "mcp_url": mcp_url,
    "api_url": api_url,
    "situacao": {
        "rotas_disponiveis": ["arm_and_takeoff", "go_to_ned", "rtl", "encerrar"],
        "no_ar": False,
        "pos_x": 0.0,
        "pos_y": 0.0,
        "pos_z": 0.0,
        "vel_x": 0.0,
        "vel_y": 0.0,
        "vel_z": 0.0,
    }
}

while True:
    comando = input("Você: ").strip()
    if not comando:
        continue
    resultado = grafo.invoke({**estado_base, "comando": comando}, config)
    if resultado.get("rota") == "encerrar":
        print("Sessão encerrada.")
        break
