import socket
import threading

from ClientRegistry import ClientRegistry

HOST = '127.0.0.1'
PORT = 12345

def handle_client(client_socket, addr):
    try:
        client_socket.sendall(b'Enter username: ')
        while True:
            username = client_socket.recv(1024).decode().strip()
            if ClientRegistry.add_client(username, client_socket):
                client_socket.sendall(f"Welcome, {username}!\n".encode())
                break
            else:
                client_socket.sendall(b"Username already taken. Try again: ")

        # Send list of currently online users
        other_users = [u for u in ClientRegistry.get_all_usernames() if u != username]
        if other_users:
            client_socket.sendall(f"Currently online: {', '.join(other_users)}\n".encode())
        else:
            client_socket.sendall(b"No one else is online.\n")

        client_socket.sendall(b"Use @username message to send private messages.\n")

        broadcast_message(f"[INFO] {username} has joined the chat.\n", exclude_username=username)

        ClientRegistry.print_clients()

        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break

            msg_str = msg.decode().strip()

            if msg_str.startswith('@'):
                parts = msg_str.split(' ', 1)
                if len(parts) < 2:
                    client_socket.sendall(b"Invalid format. Use @username message\n")
                    continue

                recipient_name = parts[0][1:]
                message_content = parts[1]

                recipient_socket = ClientRegistry.get_client_socket(recipient_name)

                if recipient_socket:
                    recipient_socket.sendall(f"[From {username}]: {message_content}\n".encode())
                    client_socket.sendall(f"[To {recipient_name}]: {message_content}\n".encode())
                else:
                    client_socket.sendall(f"User '{recipient_name}' not found.\n".encode())
            else:
                client_socket.sendall(b"Invalid message format. Use @username message\n")

    except Exception as e:
        print(f"[ERROR] Client error: {e}")
    finally:
        ClientRegistry.remove_client(username)
        broadcast_message(f"[INFO] {username} has left the chat.\n", exclude_username=username)
        client_socket.close()
        print(f"[INFO] {username} disconnected.")
        
def broadcast_message(message: str, exclude_username: str = ""):
    for user in ClientRegistry.get_all_usernames():
        if user != exclude_username:
            sock = ClientRegistry.get_client_socket(user)
            if sock:
                try:
                    sock.sendall(message.encode())
                except:
                    pass  # Ignore failures (e.g., disconnected clients)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on port {PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"New connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
