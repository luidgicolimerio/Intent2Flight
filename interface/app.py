import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
import math
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.models.missao.grafo import construir_grafo
from src.utils import langfuse_handler

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
BASE_LAT = float(os.getenv("DRONE_BASE_LAT", "-23.5505"))
BASE_LON = float(os.getenv("DRONE_BASE_LON", "-46.6333"))
st.set_page_config(layout="wide", page_title="Drone AI Co-Pilot")

# --- Inicialização ---
if "grafo" not in st.session_state:
    st.session_state.grafo = construir_grafo()
    st.session_state.thread_id = "missao-ui-1"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "frota" not in st.session_state:
    st.session_state.frota = {
        "drone_1": "disponivel",
        "drone_2": "disponivel",
        "drone_3": "disponivel",
        "drone_4": "disponivel",
    }

if "status_missao" not in st.session_state:
    st.session_state.status_missao = "aguardando"

if "plano_de_voo" not in st.session_state:
    st.session_state.plano_de_voo = []

if "aguardando_aprovacao" not in st.session_state:
    st.session_state.aguardando_aprovacao = False


# --- Conversão NED → Lat/Lon ---
def ned_to_latlon(x: float, y: float) -> tuple[float, float]:
    lat = BASE_LAT + (x / 111_320)
    lon = BASE_LON + (y / (111_320 * math.cos(math.radians(BASE_LAT))))
    return round(lat, 7), round(lon, 7)


CORES_DRONE = {
    "drone_1": "#00d4ff",
    "drone_2": "#ff6b35",
    "drone_3": "#7fff00",
    "drone_4": "#ff00ff",
}


def render_mapa(plano: list[dict]):
    # Coleta waypoints por drone
    rotas: dict[str, list[dict]] = {}
    for cmd in plano:
        alvo = cmd.get("alvo", "drone_1")
        params = cmd.get("parametros") or {}
        if cmd["acao"] in ("go_to_ned", "arm_and_takeoff"):
            lat, lon = ned_to_latlon(params.get("x", 0.0), params.get("y", 0.0))
            alt = abs(params.get("altitude", 0.0))
            rotas.setdefault(alvo, []).append({"lat": lat, "lon": lon, "alt": alt, "acao": cmd["acao"]})

    # Centro do mapa
    todos_pontos = [(BASE_LAT, BASE_LON)] + [(w["lat"], w["lon"]) for ws in rotas.values() for w in ws]
    center_lat = sum(p[0] for p in todos_pontos) / len(todos_pontos)
    center_lon = sum(p[1] for p in todos_pontos) / len(todos_pontos)

    max_delta = max(
        max(abs(p[0] - center_lat) for p in todos_pontos),
        max(abs(p[1] - center_lon) for p in todos_pontos),
        0.0001,
    )
    zoom = max(10, min(20, round(math.log2(0.1 / max_delta) + 14)))

    # Monta marcadores e polylines via Maps JavaScript API embutida no iframe
    markers_js = f"""
        new google.maps.Marker({{
            position: {{lat: {BASE_LAT}, lng: {BASE_LON}}},
            map: map,
            title: 'Base',
            label: {{ text: '🏠', fontSize: '18px' }},
            icon: {{ path: google.maps.SymbolPath.CIRCLE, scale: 0 }}
        }});
    """

    polylines_js = ""
    for drone, waypoints in rotas.items():
        cor = CORES_DRONE.get(drone, "#ffffff")
        # Polyline: base → waypoints
        path_points = [f"{{lat:{BASE_LAT}, lng:{BASE_LON}}}"] + [
            f"{{lat:{w['lat']}, lng:{w['lon']}}}" for w in waypoints
        ]
        polylines_js += f"""
        new google.maps.Polyline({{
            path: [{', '.join(path_points)}],
            map: map,
            strokeColor: '{cor}',
            strokeOpacity: 0.9,
            strokeWeight: 2,
            icons: [{{ icon: {{ path: google.maps.SymbolPath.FORWARD_OPEN_ARROW }}, offset: '100%' }}]
        }});
        """
        for i, wp in enumerate(waypoints, 1):
            markers_js += f"""
            new google.maps.Marker({{
                position: {{lat: {wp['lat']}, lng: {wp['lon']}}},
                map: map,
                title: '{drone} WP{i} — alt {wp['alt']:.0f}m',
                label: {{ text: '{i}', color: '{cor}', fontWeight: 'bold', fontSize: '12px' }},
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 8,
                    fillColor: '{cor}',
                    fillOpacity: 1,
                    strokeColor: '#fff',
                    strokeWeight: 1.5,
                }}
            }});
            """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{ margin: 0; background: #0e1117; }}
        #map {{ width: 100%; height: 420px; border-radius: 8px; }}
        #legend {{
          background: #1a1a2e; color: #ccc; font-size: 12px;
          padding: 8px 12px; font-family: monospace; line-height: 1.8;
          border-radius: 0 0 8px 8px;
        }}
      </style>
    </head>
    <body>
      <div id="map"></div>
      <div id="legend">
        {'<br>'.join(
            f'<span style="color:{CORES_DRONE.get(d, "#fff")}">●</span> <b>{d}</b>: ' +
            ' → '.join(f'WP{i+1}({w["lat"]:.5f}, {w["lon"]:.5f}) {w["alt"]:.0f}m' for i, w in enumerate(ws))
            for d, ws in rotas.items()
        ) if rotas else '📍 Nenhum plano de voo ativo — aguardando missão.'}
      </div>
      <script>
        function initMap() {{
          const map = new google.maps.Map(document.getElementById('map'), {{
            center: {{lat: {center_lat}, lng: {center_lon}}},
            zoom: {zoom},
            mapTypeId: 'satellite',
            disableDefaultUI: true,
            zoomControl: true,
          }});
          {markers_js}
          {polylines_js}
        }}
      </script>
      <script
        src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap"
        async defer>
      </script>
    </body>
    </html>
    """
    st.iframe(html, height=500)


def get_config(on_instrucao=None):
    return {
        "configurable": {
            "thread_id": st.session_state.thread_id,
            "on_instrucao": on_instrucao,
        },
        "callbacks": [langfuse_handler],
    }


async def invocar_missao(objetivo: str) -> dict:
    return await st.session_state.grafo.ainvoke(
        {
            "messages": [HumanMessage(content=objetivo)],
            "objetivo_abstrato": objetivo,
            "plano_de_voo": [],
            "comando_ativo": None,
            "situacao_frota": st.session_state.frota,
            "status_missao": None,
            "feedback_auditor": None,
        },
        get_config(),
    )


async def retomar_missao(on_instrucao=None) -> dict:
    config = get_config(on_instrucao)
    resultado = None
    while True:
        resultado = await st.session_state.grafo.ainvoke(None, config)
        state = await st.session_state.grafo.aget_state(config)
        if not state.next:
            break
    return resultado


# --- LAYOUT ---
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("🗺️ Flight Plan Map")
    render_mapa(st.session_state.plano_de_voo)

    st.subheader("🚁 Fleet Status")
    cols_frota = st.columns(4)
    for i, (drone, status) in enumerate(st.session_state.frota.items()):
        icon = "🟢" if status == "disponivel" else "🔴" if status == "falha" else "🟡"
        cols_frota[i].metric(drone.replace("_", " ").title(), f"{icon} {status}")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("🏠 RTH (Return to Home)", type="secondary", use_container_width=True)
    with c2:
        st.button("🚨 Emergency Stop", type="primary", use_container_width=True)
    with c3:
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.status_missao = "aguardando"
            st.session_state.plano_de_voo = []
            st.session_state.aguardando_aprovacao = False
            st.session_state.thread_id = f"missao-ui-{id(object())}"
            st.rerun()

with col_right:
    st.subheader("🤖 AI Co-Pilot")

    # t1, t2 = st.columns(2)
    # t1.metric("Mission Status", st.session_state.status_missao.upper())
    # t2.metric("Pending Commands", len(st.session_state.plano_de_voo))

    # st.divider()

    # if not st.session_state.aguardando_aprovacao:
    #     st.caption("💡 Try saying:")
    #     st.info(
    #         "• Decole o drone_1 e vá para as coordenadas norte 10, leste 5.\n"
    #         "• Envie dois drones para patrulhar o perímetro.\n"
    #         "• Pouse todos os drones com segurança."
    #     )

    # Container com scroll interno — a página não rola junto com as mensagens
    chat_container = st.container(height=450)

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if st.session_state.aguardando_aprovacao:
            st.warning("⚠️ Plano gerado. Revise o mapa e confirme a execução.")
            col_ok, col_cancel = st.columns(2)

            with col_ok:
                if st.button("✅ Aprovar e Executar", type="primary", use_container_width=True):
                    st.session_state.aguardando_aprovacao = False
                    with st.spinner("Executando missão..."):
                        log_placeholder = chat_container.empty()
                        log_lines = []

                        def on_instrucao(alvo, instrucao):
                            log_lines.append(f"🤖 **[{alvo}]** {instrucao}")
                            log_placeholder.markdown("\n\n".join(log_lines))

                        try:
                            resultado = asyncio.run(retomar_missao(on_instrucao))
                            status = resultado.get("status_missao", "desconhecido")
                            st.session_state.status_missao = status
                            st.session_state.plano_de_voo = resultado.get("plano_de_voo", [])
                            st.session_state.frota = resultado.get("situacao_frota", st.session_state.frota)
                            response = f"✅ Missão executada. Status final: `{status}`"
                        except Exception as e:
                            response = f"❌ Erro na execução: {e}"
                            st.session_state.status_missao = "falha"

                        log_placeholder.empty()
                        for line in log_lines:
                            st.session_state.messages.append({"role": "assistant", "content": line})
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

            with col_cancel:
                if st.button("❌ Cancelar Missão", use_container_width=True):
                    st.session_state.aguardando_aprovacao = False
                    st.session_state.status_missao = "cancelado"
                    st.session_state.plano_de_voo = []
                    st.session_state.messages.append({"role": "assistant", "content": "🚫 Missão cancelada pelo operador."})
                    st.rerun()

    # chat_input fica FORA do container para não interferir no scroll interno
    if not st.session_state.aguardando_aprovacao:
        if prompt := st.chat_input("Descreva sua missão..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with chat_container:
                with st.chat_message("user"):
                    st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Planejando missão..."):
                        try:
                            resultado = asyncio.run(invocar_missao(prompt))
                            plano = resultado.get("plano_de_voo", [])
                            status = resultado.get("status_missao", "desconhecido")
                            feedback = resultado.get("feedback_auditor")

                            st.session_state.status_missao = status
                            st.session_state.plano_de_voo = plano

                            if plano:
                                st.session_state.aguardando_aprovacao = True
                                linhas = "\n".join(
                                    f"- **{c['acao']}** → `{c.get('alvo', 'N/A')}` params: `{c.get('parametros')}`"
                                    for c in plano
                                )
                                response = (
                                    f"📋 Plano gerado com **{len(plano)} comando(s)**:\n\n{linhas}\n\n"
                                    "Revise o mapa à esquerda e confirme a execução."
                                )
                            elif feedback:
                                response = f"⚠️ Plano rejeitado pelo auditor:\n\n> {feedback}"
                            else:
                                response = f"Status: `{status}`"

                        except Exception as e:
                            response = f"❌ Erro ao planejar missão: {e}"
                            st.session_state.status_missao = "falha"

                        st.write(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
