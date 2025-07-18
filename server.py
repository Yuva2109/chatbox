import socket
import threading
import mysql.connector
import bcrypt
from ClientRegistry import ClientRegistry

HOST = '0.0.0.0'
PORT = 12345

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root12",
    database="chatbox_db"
)
cursor = db.cursor(buffered=True)

def handle_client(client_socket, addr):
    username = None
    try:
        while True:
            client_socket.sendall(b"Do you want to [signup] or [login]? ")
            action = client_socket.recv(1024).decode().strip().lower()

            if action == "signup":
                client_socket.sendall(b"Choose a username: ")
                username = client_socket.recv(1024).decode().strip()

                client_socket.sendall(b"Choose a password: ")
                password = client_socket.recv(1024).decode().strip()

                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                try:
                    cursor.execute(
                        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                        (username, hashed_pw)
                    )
                    db.commit()
                    client_socket.sendall(b"Signup successful! Please login now.\n")
                except mysql.connector.IntegrityError:
                    client_socket.sendall(b"Username already exists. Try again.\n")
                continue

            elif action == "login":
                while True:
                    client_socket.sendall(b"Username: ")
                    username = client_socket.recv(1024).decode().strip()
                    client_socket.sendall(b"Password: ")
                    password = client_socket.recv(1024).decode().strip()
                    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
                    row = cursor.fetchone()

                    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
                        client_socket.sendall(f"Welcome, {username}!\n".encode())
                        break
                    else:
                        client_socket.sendall(b"Invalid username or password. Try again.\n")
                break
            else:
                client_socket.sendall(b"Invalid option. Please type signup or login.\n")

        if not ClientRegistry.add_client(username, client_socket):
            client_socket.sendall(b"User already logged in elsewhere.\n")
            return

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
        if username:
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
                    pass

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")
    while True:
        client_socket, addr = server.accept()
        print(f"New connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
