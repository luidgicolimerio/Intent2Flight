import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from langchain_core.messages import HumanMessage
from src.models.missao.grafo import construir_grafo
from src.utils import langfuse_handler

grafo = construir_grafo()
config = {"configurable": {"thread_id": "missao-1"}}

async def main():
    print("=== Planejamento de Missão de Drones via LLM ===")

    while True:
        objetivo = input("Missão: ").strip()
        if not objetivo:
            continue

        resultado = await grafo.ainvoke(
            {
                "messages": [HumanMessage(content=objetivo)],
                "objetivo_abstrato": None,
                "plano_de_voo": [],
                "comando_ativo": None,
                "situacao_frota": {
                    "drone_1": "disponivel",
                    "drone_2": "indisponivel",
                    "drone_3": "indisponivel",
                    "drone_4": "indisponivel",
                },
                "status_missao": None,
                "feedback_auditor": None,
            },
            config | {"callbacks": [langfuse_handler]},
        )

        print(f"\nStatus final: {resultado.get('status_missao')}")
        print(f"Comandos executados: {len(resultado.get('plano_de_voo', []))} restantes na fila")

        continuar = input("\nNova missão? (s/n): ").strip().lower()
        if continuar != "s":
            print("Sessão encerrada.")
            break

asyncio.run(main())

from langchain_core.messages import HumanMessage
from src.models.missao.grafo import construir_grafo
from src.utils import langfuse_handler

grafo = construir_grafo()
config = {"configurable": {"thread_id": "missao-1"}}

print("=== Planejamento de Missão de Drones via LLM ===")

while True:
    objetivo = input("Missão: ").strip()
    if not objetivo:
        continue

    resultado = grafo.invoke(
        {
            "messages": [HumanMessage(content=objetivo)],
            "objetivo_abstrato": None,
            "plano_de_voo": [],
            "comando_ativo": None,
            "situacao_frota": {
                "drone_1": "disponivel",
                "drone_2": "disponivel",
                "drone_3": "disponivel",
                "drone_4": "disponivel",
            },
            "status_missao": None,
            "feedback_auditor": None,
        },
        config | {"callbacks": [langfuse_handler]},
    )

    print(f"\nStatus final: {resultado.get('status_missao')}")
    print(f"Comandos executados: {len(resultado.get('plano_de_voo', []))} restantes na fila")

    continuar = input("\nNova missão? (s/n): ").strip().lower()
    if continuar != "s":
        print("Sessão encerrada.")
        break
