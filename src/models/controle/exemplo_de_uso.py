import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from langgraph.types import Command
from src.models.controle.grafo import construir_grafo
from src.utils import langfuse_handler

grafo = construir_grafo()
config = {"configurable": {"thread_id": "drone-1"}}

print("=== Controle de Drone via LLM ===")

grafo.invoke({
    "comando": "",
    "messages": [],
    "rota": None,
    "resultado_api": None,
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
}, config | {"callbacks": [langfuse_handler]})

while True:
    comando = input("Você: ").strip()
    if not comando:
        continue
    resultado = grafo.invoke(Command(resume=comando), config | {"callbacks": [langfuse_handler]})
    if resultado.get("rota") == "rtl":
        print("Sessão encerrada.")
        break
