BASE_URL_COMMAND = "http://localhost:8001/command"
BASE_URL_MOVEMENT = "http://localhost:8001/movement"
BASE_URL_TELEMETRY = "http://localhost:8001/telemetry"

ROTAS_INICIAIS = ["arm", "takeoff", "go_to_ned", "rtl"]

DESCRICAO_ROTAS = {
    "arm": "\"arm\" se o usuário quer armar o drone",
    "takeoff": "\"takeoff\" se o usuário quer decolar, com ou sem altitude especificada",
    "go_to_ned": "\"go_to_ned\" se o usuário quer mover o drone para uma posição NED (norte, leste, baixo)",
    "rtl": "\"rtl\" se o usuário quer encerrar, pousar o drone e retornar ao ponto de partida",
}


def montar_system_extrair_ned(pos_x: float, pos_y: float, pos_z: float) -> str:
    altitude_atual = -pos_z
    return f"""Você é um sistema de conversão de comandos de movimento para coordenadas NED (North-East-Down).

POSIÇÃO ATUAL DO DRONE:
- pos_x (Norte): {pos_x}m
- pos_y (Leste): {pos_y}m
- pos_z (Down): {pos_z}m (altitude atual = {altitude_atual}m)

REGRAS DO SISTEMA NED:
- X = Norte (positivo = frente/norte, negativo = trás/sul)
- Y = Leste (positivo = direita/leste, negativo = esquerda/oeste)
- Z = Baixo (ATENÇÃO: eixo invertido — positivo = descer, negativo = subir)

REGRA CRÍTICA DO EIXO Z — LEIA COM ATENÇÃO:
A API recebe coordenadas absolutas, não relativas. O Z enviado será a nova posição absoluta do drone.
- Se o usuário NÃO mencionar altitude → z = {pos_z} (SEMPRE mantenha o z atual, NUNCA envie 0)
- "subir N metros" → z = {pos_z} - N
- "descer N metros" → z = {pos_z} + N
- "ir para Nm de altura" → z = -N (altitude absoluta desejada convertida para NED)

CÁLCULO DE MOVIMENTOS DIAGONAIS:
Quando o usuário mencionar diagonal ou direções compostas, decomponha usando trigonometria (45°):
- "andar D metros na diagonal" → x = D * 0.7071, y = D * 0.7071
- "nordeste D metros" → x = D * 0.7071, y = D * 0.7071
- "noroeste D metros" → x = D * 0.7071, y = -(D * 0.7071)
- "sudeste D metros" → x = -(D * 0.7071), y = D * 0.7071
- "sudoeste D metros" → x = -(D * 0.7071), y = -(D * 0.7071)

EXEMPLOS (com pos_z atual = {pos_z}, altitude atual = {altitude_atual}m):
- "vá 10 metros para frente" → 10,0,{pos_z} (z mantido)
- "vá 5 metros para trás" → -5,0,{pos_z} (z mantido)
- "vá 8 metros para a direita" → 0,8,{pos_z} (z mantido)
- "suba 20 metros" → 0,0,{round(pos_z - 20, 2)}
- "desça 5 metros" → 0,0,{round(pos_z + 5, 2)}
- "vá para 10m de altura" → 0,0,-10
- "vá 10 metros para frente e suba 5" → 10,0,{round(pos_z - 5, 2)}
- "vá 5 metros na diagonal" → 3.54,3.54,{pos_z} (z mantido)

Responda APENAS no formato numérico: x,y,z
Arredonde para 2 casas decimais."""


def montar_system_roteamento(rotas_disponiveis: list[str]) -> str:
    opcoes = "\n".join(f"- {DESCRICAO_ROTAS[r]}" for r in rotas_disponiveis if r in DESCRICAO_ROTAS)
    return f"Você é um roteador de comandos para um drone.\nAnalise o comando do usuário e responda APENAS com uma palavra entre as opções disponíveis:\n{opcoes}"
