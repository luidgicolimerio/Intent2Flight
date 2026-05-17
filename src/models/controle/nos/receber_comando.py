from langchain_core.messages import HumanMessage
from ..estado import Estado


def receber_comando(estado: Estado) -> dict:
    novo_comando = estado["comando"]
    print(f"\n[receber_comando] Comando recebido: '{novo_comando}'")
    return {"messages": [HumanMessage(content=novo_comando)]}
