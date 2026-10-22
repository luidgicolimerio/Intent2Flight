---
name: gps-follower
description: Utilize esta skill para executar e compreender o script gps_follower.py, que faz um drone seguidor rastrear a posição de um drone líder usando offsets espaciais configuráveis.
---

# gps-follower

## Overview

Esta skill explica como configurar, executar e entender o fluxo de funcionamento do script de rastreamento de drones (`gps_follower.py`)[cite: 1]. Ele permite que um veículo seguidor acompanhe um líder em tempo real baseado em telemetria GPS e distâncias relativas pré-definidas[cite: 1].

## Instructions

### 1. Preparar o ambiente e as dependências

Certifique-se de que o arquivo `flight_helpers.py` está presente no diretório superior (ou configurado no `sys.path`), pois o script depende dele para funções vitais como `create_session`, `send_command` e `get_home_gps`[cite: 1]. Você precisará de duas instâncias de API rodando simultaneamente: uma para o líder e outra para o seguidor[cite: 1].

### 2. Configurar os parâmetros de distanciamento

Ao invocar o script via linha de comando, defina a posição relativa (offset) que o seguidor deve manter em relação ao líder[cite: 1]:

*   `--leader-url`: Especifique o host e porta da API do líder (o padrão é `localhost:8001`)[cite: 1].
*   `--offset-north`: Defina a distância no eixo Norte em metros. Para fazer o seguidor voar *atrás* do líder, use valores negativos (padrão: `-3`)[cite: 1].
*   `--offset-east`: Defina o distanciamento no eixo Leste em metros (padrão: `0`)[cite: 1].
*   `--offset-alt`: Defina a altitude do seguidor acima da altitude do líder em metros (padrão: `2.0`)[cite: 1].

### 3. Compreender e monitorar o fluxo de execução

Após iniciar o script, ele seguirá um fluxo de duas etapas principais[cite: 1]:

*   **Setup Inicial:** O script armará o drone seguidor, fará a leitura da altitude base (*home altitude*) de ambos os drones para equalizar diferenças de barômetro, e comandará a decolagem do seguidor[cite: 1].
*   **Loop de Rastreamento (2 Hz):** A cada 0.5 segundos, o script captura as coordenadas GPS (latitude, longitude e altitude) do líder[cite: 1]. Ele calcula as novas coordenadas alvo do seguidor através de uma aproximação de Haversine e envia o comando `/movement/go_to_gps` para posicionar o veículo[cite: 1].

Para interromper a execução, utilize `Ctrl+C`. O script possui um *graceful shutdown* configurado que garantirá que o drone seguidor receba um comando de *Return to Launch* (RTL) antes de sair do programa[cite: 1].

> **⚠️ Disclaimer:** Este script roda por tempo **indeterminado** — ele não termina sozinho. Ao ser invocado via `run_skill`, o processo é iniciado em background e o agente **não aguarda sua conclusão**. O script continuará executando até ser interrompido externamente (sinal SIGTERM/SIGINT) ou até que o drone receba um comando RTL.