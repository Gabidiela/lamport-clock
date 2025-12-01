import socket
import threading
import json
import time
import random
import sys

class LamportClock:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.value += 1
            return self.value

    def update(self, received_time):
        with self.lock:
            self.value = max(self.value, received_time) + 1
            return self.value

    def get_time(self):
        with self.lock:
            return self.value

class Worker:
    def __init__(self, process_id, config_file='config.json'):
        self.process_id = process_id
        self.clock = LamportClock()
        self.running = True

        # Load Config
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.my_config = next((w for w in self.config['workers'] if w['id'] == process_id), None)
        if not self.my_config:
            raise ValueError(f"ID {process_id} não encontrado na configuração.")

        self.peers = [w for w in self.config['workers'] if w['id'] != process_id]

        # Monitor Connection
        self.monitor_socket = None
        self.connect_to_monitor()

    def connect_to_monitor(self):
        try:
            self.monitor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.monitor_socket.connect((self.config['monitor']['host'], self.config['monitor']['port']))
        except Exception as e:
            print(f"[Processo {self.process_id}] Falha ao conectar no Monitor: {e}")
            self.monitor_socket = None

    def log(self, message):
        timestamp = self.clock.get_time()
        formatted_msg = f"Processo {self.process_id} | Clock: {timestamp} | {message}"
        print(formatted_msg)

        if self.monitor_socket:
            try:
                self.monitor_socket.sendall((formatted_msg + "\n").encode('utf-8'))
            except:
                # Tenta reconectar se falhar
                self.connect_to_monitor()
                if self.monitor_socket:
                    try:
                        self.monitor_socket.sendall((formatted_msg + "\n").encode('utf-8'))
                    except:
                        pass

    def listen_for_messages(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.my_config['host'], self.my_config['port']))
        server.listen()

        while self.running:
            try:
                server.settimeout(1.0) # Timeout para verificar self.running periodicamente
                conn, addr = server.accept()
                threading.Thread(target=self.handle_peer_message, args=(conn,)).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[Processo {self.process_id}] Erro no servidor: {e}")

    def handle_peer_message(self, conn):
        try:
            data = conn.recv(1024)
            if data:
                msg = json.loads(data.decode('utf-8'))
                received_clock = msg['clock']
                sender_id = msg['pid']

                self.clock.update(received_clock)
                self.log(f"RECEBIDO de Processo {sender_id} (Clock msg: {received_clock})")
        except Exception as e:
            print(f"[Processo {self.process_id}] Erro ao processar mensagem: {e}")
        finally:
            conn.close()

    def send_message(self):
        if not self.peers:
            return

        target = random.choice(self.peers)
        self.clock.increment() # Incrementa antes de enviar

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target['host'], target['port']))

            msg = {'pid': self.process_id, 'clock': self.clock.get_time()}
            s.sendall(json.dumps(msg).encode('utf-8'))
            s.close()

            self.log(f"ENVIADO para Processo {target['id']}")
        except Exception as e:
            self.log(f"FALHA ao enviar para Processo {target['id']}: {e}")

    def run(self):
        # Inicia thread do servidor (para receber mensagens)
        server_thread = threading.Thread(target=self.listen_for_messages)
        server_thread.start()

        self.log("Iniciado")

        try:
            while True:
                time.sleep(random.uniform(1.0, 3.0)) # Intervalo aleatório

                action = random.choice(['internal', 'send'])

                if action == 'internal':
                    self.clock.increment()
                    self.log("EVENTO INTERNO")
                else:
                    self.send_message()

        except KeyboardInterrupt:
            self.running = False
            self.log("Encerrando...")
            if self.monitor_socket:
                self.monitor_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python worker.py <process_id>")
        sys.exit(1)

    pid = int(sys.argv[1])
    worker = Worker(pid)
    worker.run()
