from langgraph.types import interrupt
from langchain_core.messages import HumanMessage
from ..estado import Estado


def receber_comando(estado: Estado) -> dict:
    print("\n[receber_comando] Aguardando comando...")
    novo_comando = interrupt("Aguardando comando do usuário: ")
    print(f"[receber_comando] Comando recebido: '{novo_comando}'")
    return {"comando": novo_comando, "messages": [HumanMessage(content=novo_comando)]}
