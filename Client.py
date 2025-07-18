import socket
import threading

SERVER_HOST = '10.126.181.97'
SERVER_PORT = 12345

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(msg)
        except Exception as e:
            print(f"[ERROR] Connection lost: {e}")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        # Receive username prompt
        server_msg = client.recv(1024).decode()
        print(server_msg, end='')
        username = input()
        client.sendall(username.encode())

        # Receive server response to username
        while True:
            response = client.recv(1024).decode()
            print(response, end='')
            if "Welcome" in response:
                break
            username = input()
            client.sendall(username.encode())

        # Print additional instructions
        print("You can now send private messages using the format: @username message")
        print("Type 'exit' to leave the chat.")

        # Start background listener
        threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

        while True:
            msg = input()
            if msg.lower() == 'exit':
                break
            client.sendall(msg.encode())

    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
    finally:
        client.close()
        print("Disconnected.")

if __name__ == "__main__":
    main()
