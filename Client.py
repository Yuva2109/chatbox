import socket
import threading

SERVER_HOST = '10.137.245.137'
SERVER_PORT = 12345

def receive_messages(sock):
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode())
    except:
        pass
    finally:
        sock.close()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        # Example: receive prompt to signup/login
        while True:
            server_msg = client.recv(1024).decode()
            print(server_msg, end='')
            choice = input()
            client.sendall(choice.encode())
            if choice.lower() == 'login':
                break  # Assuming you skip signup for now

        # Example: receive username prompt
        server_msg = client.recv(1024).decode()
        print(server_msg, end='')
        username = input()
        client.sendall(username.encode())

        # Receive password prompt
        server_msg = client.recv(1024).decode()
        print(server_msg, end='')
        password = input()
        client.sendall(password.encode())

        # Wait for server welcome or retry loop
        while True:
            response = client.recv(1024).decode()
            print(response, end='')
            if "Welcome" in response:
                break
            # Prompt again if wrong
            server_msg = client.recv(1024).decode()
            print(server_msg, end='')
            username = input()
            client.sendall(username.encode())
            server_msg = client.recv(1024).decode()
            print(server_msg, end='')
            password = input()
            client.sendall(password.encode())

        print("You can now send private messages using @username message")
        print("Type 'exit' to leave the chat.")

        # Start background listener
        threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

        while True:
            msg = input()
            if msg.lower() == 'exit':
                client.close()
                break
            client.sendall(msg.encode())

    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
    finally:
        client.close()
        print("Disconnected.")

if __name__ == "__main__":
    main()
