from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from src.config import llm

TOOLS_POR_ROTA = {
    "arm_and_takeoff": {"arm_and_takeoff", "get_ned"},
    "go_to_ned":       {"go_to_ned", "get_ned"},
    "rtl":             {"rtl", "get_ned"},
}

async def agente_roteamento(system_prompt: str, comando: str, callbacks=None) -> str:
    agente = create_react_agent(llm, [], prompt=system_prompt)
    resposta = await agente.ainvoke(
        {"messages": [{"role": "user", "content": comando}]},
        config={"callbacks": callbacks} if callbacks else {},
    )
    return resposta["messages"][-1].content.strip().lower()

async def agente_telemetria(mcp_url: str, callbacks=None) -> dict:
    porta = mcp_url.split(":")[-1].replace("/mcp", "")
    nome_servidor = f"uav_{porta}"
    
    client = MultiServerMCPClient({nome_servidor: {"url": mcp_url, "transport": "http"}})
    todas_tools = await client.get_tools()
    
    tools = [t for t in todas_tools if t.name == "get_ned"]
    agente = create_react_agent(llm, tools)
    
    resposta = await agente.ainvoke(
        {"messages": [{"role": "user", "content": "Busque a posição e velocidade atual do drone via get_ned."}]},
        config={"callbacks": callbacks} if callbacks else {},
    )
    return resposta

async def agente_piloto(mcp_url: str, system_prompt: str, rota: str, comando: str, callbacks=None) -> dict:
    porta = mcp_url.split(":")[-1].replace("/mcp", "")
    nome_servidor = f"uav_{porta}"
    
    client = MultiServerMCPClient({nome_servidor: {"url": mcp_url, "transport": "http"}})
    todas_tools = await client.get_tools()
    
    tools_permitidas = TOOLS_POR_ROTA.get(rota, set())
    tools = [t for t in todas_tools if t.name in tools_permitidas]
    
    agente = create_react_agent(llm, tools, prompt=system_prompt)
    return await agente.ainvoke(
        {"messages": [{"role": "user", "content": comando}]},
        config={"callbacks": callbacks} if callbacks else {},
    )