import socket
import threading

def receive_message():
    room = "_main_"
    while True:
        room_name = client_socket.recv(1024).decode('utf-8')
        message = client_socket.recv(1024)
        if message and room_name == room:
            print(message.decode('utf-8'))

def start_client():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    user = input("Enter your username: ")
    client_socket.sendall(user.encode('utf-8'))

    client_socket.sendall("_JOIN_MAIN".encode('utf-8'))

    thread = threading.Thread(target=receive_message)
    thread.start()

    while True:
        message = input(f"{user}: ")
        client_socket.sendall(message.encode('utf-8'))

if __name__ == "__main__":
    start_client()

