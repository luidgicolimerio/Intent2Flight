from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class SituacaoDrone(TypedDict):
    pos_x: float
    pos_y: float
    pos_z: float
    vel_x: float
    vel_y: float
    vel_z: float
    rotas_disponiveis: list[str]
    no_ar: bool


class Estado(TypedDict):
    messages: Annotated[list, add_messages]
    comando: str
    rota: str | None
    resultado_api: dict | None
    situacao: SituacaoDrone
