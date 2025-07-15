import socket
import threading

SERVER_HOST = '127.0.0.1'  
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

        threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

        while True:
            server_msg = client.recv(1024).decode()
            print(server_msg, end='') 
            username = input()
            client.sendall(username.encode())
            response = client.recv(1024).decode()
            print(response, end='')  
            if "Welcome" in response:
                break

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
