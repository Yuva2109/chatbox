# client_handler.py

import threading
import socket
from ClientRegistry import ClientRegistry

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, username):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.username = username
        self.alive = True

    def run(self):
        try:
            welcome = f"[Server] Welcome {self.username}! Type messages in 'recipient:message' format."
            self.conn.send(welcome.encode())

            while self.alive:
                message = self.conn.recv(1024).decode().strip()
                if not message:
                    continue
                if ":" not in message:
                    self.conn.send("[Server] Invalid format. Use 'username:message'.".encode())
                    continue

                target, msg = message.split(":", 1)
                target = target.strip()
                msg = msg.strip()

                receiver_conn = ClientRegistry.get_client_socket(target)
                if receiver_conn:
                    try:
                        full_msg = f"{self.username}: {msg}"
                        receiver_conn.send(full_msg.encode())
                    except Exception:
                        self.conn.send(f"[Server] Failed to deliver message to {target}.".encode())
                else:
                    self.conn.send(f"[Server] User '{target}' not found.".encode())
        except Exception as e:
            print(f"[Error] Client {self.username} connection error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        print(f"[Server] {self.username} disconnected.")
        self.alive = False
        ClientRegistry.remove_client(self.username)
        self.conn.close()
