import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio
import json
import os
from dotenv import load_dotenv
import websockets
from langchain_core.messages import HumanMessage
from src.models.missao.grafo import construir_grafo
from src.utils import langfuse_handler

load_dotenv()
HOST = "localhost"
PORT = int(os.getenv("LLM_SERVER_PORT", 8010))

FROTA_INICIAL = {
    "drone_1": "disponivel",
    "drone_2": "disponivel",
    "drone_3": "disponivel",
    "drone_4": "disponivel",
}


def make_on_instrucao(websocket, loop):
    def on_instrucao(alvo, instrucao):
        asyncio.run_coroutine_threadsafe(
            websocket.send(json.dumps({"type": "instrucao", "text": f"[{alvo}] {instrucao}"})),
            loop,
        )
    return on_instrucao


async def handler(websocket):
    grafo = construir_grafo()
    thread_id = f"gs-{id(websocket)}"
    loop = asyncio.get_event_loop()
    aguardando_aprovacao = False

    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [langfuse_handler],
    }

    async for raw in websocket:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            await websocket.send(json.dumps({"type": "erro", "text": "Mensagem inválida."}))
            continue

        action = msg.get("action")

        if action == "missao":
            objetivo = msg.get("objetivo", "")
            await websocket.send(json.dumps({"type": "status", "text": "Planejando…"}))
            try:
                resultado = await grafo.ainvoke(
                    {
                        "messages": [HumanMessage(content=objetivo)],
                        "objetivo_abstrato": objetivo,
                        "plano_de_voo": [],
                        "comando_ativo": None,
                        "situacao_frota": FROTA_INICIAL,
                        "status_missao": None,
                        "feedback_auditor": None,
                    },
                    config,
                )
                plano = resultado.get("plano_de_voo", [])
                feedback = resultado.get("feedback_auditor")

                if plano:
                    aguardando_aprovacao = True
                    await websocket.send(json.dumps({"type": "plano", "plano": plano}))
                else:
                    await websocket.send(json.dumps({"type": "rejeitado", "text": feedback or "Plano rejeitado."}))
            except Exception as e:
                await websocket.send(json.dumps({"type": "erro", "text": str(e)}))

        elif action == "aprovar":
            if not aguardando_aprovacao:
                await websocket.send(json.dumps({"type": "erro", "text": "Nenhum plano pendente."}))
                continue

            aguardando_aprovacao = False
            await websocket.send(json.dumps({"type": "status", "text": "Executando…"}))

            config_exec = {
                "configurable": {
                    "thread_id": thread_id,
                    "on_instrucao": make_on_instrucao(websocket, loop),
                },
                "callbacks": [langfuse_handler],
            }

            try:
                while True:
                    resultado = await grafo.ainvoke(None, config_exec)
                    state = await grafo.aget_state(config_exec)
                    if not state.next:
                        break
                status = resultado.get("status_missao", "concluido")
                await websocket.send(json.dumps({"type": "concluido", "text": f"Missão encerrada. Status: {status}"}))
            except Exception as e:
                await websocket.send(json.dumps({"type": "erro", "text": str(e)}))

        elif action == "cancelar":
            aguardando_aprovacao = False
            await websocket.send(json.dumps({"type": "cancelado", "text": "Missão cancelada."}))


async def main():
    async with websockets.serve(handler, HOST, PORT):
        print(f"drone_llm WebSocket server listening on ws://{HOST}:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
