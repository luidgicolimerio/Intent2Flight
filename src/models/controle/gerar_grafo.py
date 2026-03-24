import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.models.controle.grafo import construir_grafo

grafo = construir_grafo()

with open("grafo.png", "wb") as f:
    f.write(grafo.get_graph().draw_mermaid_png())
