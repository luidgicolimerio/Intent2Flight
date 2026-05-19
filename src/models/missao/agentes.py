import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage
from src.config import llm
from src.utils import langfuse_handler

_env = Environment(loader=FileSystemLoader(Path(__file__).parent / "prompts"))


def _render(template: str, **kwargs) -> str:
    return _env.get_template(template).render(**kwargs)


async def agente_planejador(objetivo_abstrato: str, situacao_frota: dict, feedback_auditor: str | None) -> list[dict]:
    system = _render("planejador.jinja2",
                     situacao_frota=situacao_frota,
                     objetivo_abstrato=objetivo_abstrato,
                     feedback_auditor=feedback_auditor)
    resposta = await llm.ainvoke([SystemMessage(content=system),
                                  HumanMessage(content=objetivo_abstrato)],
                                  config={"callbacks": [langfuse_handler]})

    texto_limpo = resposta.content.strip()

    if texto_limpo.startswith("```json"):
        texto_limpo = texto_limpo.replace("```json", "").replace("```", "").strip()
    elif texto_limpo.startswith("```"):
        texto_limpo = texto_limpo.replace("```", "").strip()

    dados = json.loads(texto_limpo)
    return dados["plano_de_voo"]


async def agente_auditor(plano_de_voo: list[dict], situacao_frota: dict) -> dict:
    system = _render("auditor.jinja2",
                     plano_de_voo=json.dumps(plano_de_voo, ensure_ascii=False),
                     situacao_frota=situacao_frota)
    resposta = await llm.ainvoke([SystemMessage(content=system),
                                  HumanMessage(content="Avalie o plano.")],
                                  config={"callbacks": [langfuse_handler]})
    return json.loads(resposta.content)


async def agente_operador(comando_ativo: dict) -> str:
    system = _render("operador.jinja2", comando_ativo=comando_ativo)
    resposta = await llm.ainvoke([SystemMessage(content=system),
                                  HumanMessage(content="Gere a instrução.")],
                                  config={"callbacks": [langfuse_handler]})
    return resposta.content.strip()
