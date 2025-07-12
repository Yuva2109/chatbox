import socket       # It as tools used to create TCP modules
import threading    # Handle multiple users at same time

from ClientRegistry import ClientRegistry 

HOST = '127.0.0.1'    # server IP address "time being localhost"
PORT = 12345          # From which clients are connected

def handle_client(client_socket, addr):    #socket object & ip adr of cilent
    try:
        client_socket.sendall(b'Enter username: ')  # message to client side , sendall() used to tranfers every bytes 
        while True:
                username = client_socket.recv(1024).decode().strip()  # to receive data from client and convert it to string without whitespaces
                if ClientRegistry.add_client(username, client_socket):  
                    client_socket.sendall(f"Welcome, {username}!\n".encode())   # sends msg to client (not neccessary)
                    break
                else:
                    client_socket.sendall(b"Username already taken. Try again: ")

        ClientRegistry.print_clients()    # displays current online clients

        while True:
            msg = client_socket.recv(1024)
            if not msg: # if received empty msg "b''"
                break  # Client disconnected
            print(f"{username} says: {msg.decode().strip()}")  # displays the sender in server console 

    except Exception as e:
        print(f"[ERROR] Client error: {e}")
    finally:
        ClientRegistry.remove_client(username) # removes the inactive client from client registry
        client_socket.close()                    # connected socket is removed
        print(f"[INFO] {username} disconnected.") 

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket object with ipv4 adrs and TCP stream
    server.bind((HOST, PORT))  # connects can be accepted after binding host and port
    server.listen()   # waits from connection request
    print(f"Server started on port {PORT}")

    while True:
        client_socket, addr = server.accept() # server socket moved to client socket now server object is free to receive nxt client
        print(f"New connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))  # calls handle_client function
        thread.start()  # during processing of one clients request thread should not wait thats why it is used

if __name__ == "__main__":  # runs the imported file only on execution
    start_server()
