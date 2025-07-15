import socket
import threading

class ClientRegistry:
    _client_map = {}
    _lock = threading.Lock()

    @classmethod
    def add_client(cls, username: str, client_socket: socket.socket) -> bool:
        with cls._lock:
            if username not in cls._client_map:
                cls._client_map[username] = client_socket
                return True
            return False

    @classmethod
    def remove_client(cls, username: str):
        with cls._lock:
            cls._client_map.pop(username, None)

    @classmethod
    def get_client_socket(cls, username: str) -> socket.socket | None:
        with cls._lock:
            return cls._client_map.get(username)

    @classmethod
    def username_exists(cls, username: str) -> bool:
        with cls._lock:
            return username in cls._client_map

    @classmethod
    def get_all_usernames(cls):
        with cls._lock:
            return list(cls._client_map.keys())

    @classmethod
    def print_clients(cls):
        with cls._lock:
            print(f"Connected clients: {list(cls._client_map.keys())}")
