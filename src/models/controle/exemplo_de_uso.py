import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from langgraph.types import Command
from src.models.controle.grafo import construir_grafo

grafo = construir_grafo()
config = {"configurable": {"thread_id": "drone-1"}}

print("=== Controle de Drone via LLM ===")

grafo.invoke({
    "comando": "",
    "messages": [],
    "rota": None,
    "resultado_api": None,
    "situacao": {
        "rotas_disponiveis": ["arm", "takeoff", "go_to_ned", "rtl"],
        "pos_x": 0.0,
        "pos_y": 0.0,
        "pos_z": 0.0,
        "vel_x": 0.0,
        "vel_y": 0.0,
        "vel_z": 0.0,
    }
}, config)

while True:
    comando = input("Você: ").strip()
    if not comando:
        continue
    resultado = grafo.invoke(Command(resume=comando), config)
    if resultado.get("rota") == "rtl":
        print("Sessão encerrada.")
        break
