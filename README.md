# Simulação do Relógio de Lamport

Este projeto é uma implementação em Python para demonstrar o funcionamento do algoritmo de **Relógios Lógicos de Lamport** em um sistema distribuído. A aplicação utiliza sockets TCP para comunicação entre processos e um monitor centralizado para visualização dos logs e ordem dos eventos.

## Como Funciona

O algoritmo de Lamport permite ordenar eventos em um sistema distribuído sem a necessidade de um relógio físico globalmente sincronizado. Cada processo mantém um contador (relógio lógico) que obedece às seguintes regras:

1.  **Evento Interno:** Antes de executar um evento interno, o processo incrementa seu relógio: `C = C + 1`.
2.  **Envio de Mensagem:** Antes de enviar uma mensagem, o processo incrementa seu relógio (`C = C + 1`) e envia o novo valor junto com a mensagem.
3.  **Recebimento de Mensagem:** Ao receber uma mensagem com um carimbo de tempo `C_msg`, o processo atualiza seu relógio para ser maior que o atual e o recebido: `C = max(C, C_msg) + 1`.

### Arquitetura

O projeto é composto por três componentes principais:

*   **Worker (`worker.py`):** Representa um nó no sistema distribuído.
    *   Mantém seu próprio Relógio de Lamport.
    *   Realiza eventos aleatórios (internos ou envio de mensagens para outros Workers).
    *   Conecta-se a outros Workers via TCP.
    *   Envia logs de suas ações para o Monitor.
*   **Monitor (`monitor.py`):** Um servidor centralizado que recebe logs de todos os Workers e os imprime no terminal. Isso facilita a visualização do que está acontecendo em tempo real.
*   **Orchestrator (`run_simulation.py`):** Um script utilitário que lê a configuração e inicia automaticamente o Monitor e os processos Worker.

## Configuração

A topologia da rede é definida no arquivo `config.json`. Você pode adicionar ou remover Workers e alterar portas conforme necessário.

Exemplo de `config.json`:

```json
{
    "monitor": {
        "host": "127.0.0.1",
        "port": 6000
    },
    "workers": [
        { "id": 1, "host": "127.0.0.1", "port": 5001 },
        { "id": 2, "host": "127.0.0.1", "port": 5002 },
        { "id": 3, "host": "127.0.0.1", "port": 5003 }
    ]
}
```

## Como Executar

### Pré-requisitos

*   Python 3 instalado.
*   Sistemas baseados em Unix (Linux/macOS) recomendados (devido ao uso de sinais para encerramento), mas funciona em Windows com adaptações manuais.

### Passo a Passo

1.  Certifique-se de que as portas configuradas no `config.json` estão livres.
2.  Execute o script de orquestração:

    ```bash
    python3 run_simulation.py
    ```

3.  Você verá a saída do **Monitor** no terminal, mostrando os eventos de todos os processos:

    ```text
    [Monitor] Iniciado em 127.0.0.1:6000. Aguardando logs...
    [Log Centralizado] Processo 1 | Clock: 1 | Iniciado
    [Log Centralizado] Processo 2 | Clock: 1 | Iniciado
    ...
    [Log Centralizado] Processo 1 | Clock: 2 | EVENTO INTERNO
    [Log Centralizado] Processo 1 | Clock: 3 | ENVIADO para Processo 2
    [Log Centralizado] Processo 2 | Clock: 4 | RECEBIDO de Processo 1 (Clock msg: 3)
    ```

4.  Para encerrar a simulação, pressione `Ctrl+C`. O orquestrador cuidará de finalizar todos os processos abertos.

## Execução Manual (Opcional)

Se preferir rodar cada processo em um terminal separado (útil para debug):

1.  Terminal 1 (Monitor):
    ```bash
    python3 monitor.py
    ```
2.  Terminal 2 (Worker 1):
    ```bash
    python3 worker.py 1
    ```
3.  Terminal 3 (Worker 2):
    ```bash
    python3 worker.py 2
    ```
    (E assim por diante para os outros IDs definidos no config).
