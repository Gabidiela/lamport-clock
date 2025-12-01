import subprocess
import time
import json
import signal
import sys

processes = []

def cleanup(sig, frame):
    print("\n[Orchestrator] Encerrando processos...")
    for p in processes:
        p.terminate()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup)

    print("[Orchestrator] Lendo configuração...")
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Iniciar Monitor
    print("[Orchestrator] Iniciando Monitor...")
    monitor_proc = subprocess.Popen(['python3', 'monitor.py'])
    processes.append(monitor_proc)

    time.sleep(2) # Dar tempo para o monitor subir

    # Iniciar Workers
    workers_config = config['workers']
    for w in workers_config:
        pid = w['id']
        print(f"[Orchestrator] Iniciando Worker {pid}...")
        p = subprocess.Popen(['python3', 'worker.py', str(pid)])
        processes.append(p)

    print("[Orchestrator] Todos os processos iniciados. Pressione Ctrl+C para encerrar.")

    # Manter o script rodando
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
