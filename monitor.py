import socket
import threading
import json
import sys

def handle_client(conn, addr):
    print(f"[Monitor] Conexão estabelecida com {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            # Decodifica e imprime a mensagem de log
            # Assumindo que as mensagens vêm como texto puro codificado em utf-8
            msg = data.decode('utf-8').strip()
            if msg:
                print(f"[Log Centralizado] {msg}")
    except ConnectionResetError:
        pass
    except Exception as e:
        print(f"[Monitor] Erro na conexão com {addr}: {e}")
    finally:
        conn.close()
        print(f"[Monitor] Conexão fechada com {addr}")

def start_monitor(config_file='config.json'):
    with open(config_file, 'r') as f:
        config = json.load(f)

    host = config['monitor']['host']
    port = config['monitor']['port']

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((host, port))
        server.listen()
        print(f"[Monitor] Iniciado em {host}:{port}. Aguardando logs...")

        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[Monitor] Encerrando...")
    finally:
        server.close()

if __name__ == "__main__":
    start_monitor()
