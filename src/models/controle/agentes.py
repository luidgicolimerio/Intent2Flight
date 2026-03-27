from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from src.config import llm

#TODO bindar somente rotas necessárias para cada agente
async def agente_roteamento(mcp_url: str, system_prompt: str, comando: str) -> str:
    client = MultiServerMCPClient({"uav": {"url": mcp_url, "transport": "http"}})
    tools = await client.get_tools()
    agente = create_react_agent(llm, tools, prompt=system_prompt)
    resposta = await agente.ainvoke({"messages": [{"role": "user", "content": comando}]})
    return resposta["messages"][-1].content.strip().lower()


async def agente_piloto(mcp_url: str, system_prompt: str, comando: str) -> dict:
    client = MultiServerMCPClient({"uav": {"url": mcp_url, "transport": "http"}})
    tools = await client.get_tools()
    agente = create_react_agent(llm, tools, prompt=system_prompt)
    return await agente.ainvoke({"messages": [{"role": "user", "content": comando}]})
