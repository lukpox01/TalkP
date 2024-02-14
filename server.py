import socket
import threading

def handle_client(client_socket, user):
    while True:
        instruction = client_socket.recv(1024).decode('utf-8')
        room = "_main_"
        if instruction == "_JOIN_MAIN":
            print(instruction)

            rooms[room].clients.append({user: client_socket})
            while True:
                message = client_socket.recv(1024)
                if message:

                    if message == "!EXIT".encode("utf-8"):
                        rooms[room].clients.remove({user: client_socket})
                        broadcast(f"{user} has left the room {room}", user, room)
                        break

                    print(f"Received message from {user}: {message.decode('utf-8')}")
                    broadcast(message.decode('utf-8'), user, room)
                else:
                    client_socket.close()
                    break
        elif instruction == "_DISCONNECT":
            del clients[user]
            client_socket.close()
            break

def broadcast(message, user, room):
    for client in rooms[room].clients:
        # if list(client.keys())[0] != user:
        list(client.values())[0].sendall(f"{room}".encode('utf-8'))
        list(client.values())[0].sendall(f"{user}: {message}".encode('utf-8'))

def start_server():
    rooms["_main_"] = Room("_main_")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen()
    print("Server is listening on port 12345...")

    while True:
        client_socket, client_address = server_socket.accept()
        user = client_socket.recv(1024).decode('utf-8')
        if user:
            clients[user] = client_socket
            print(f"Accepted new connection from {user}@{client_address[0]}:{client_address[1]}")
            thread = threading.Thread(target=handle_client, args=(client_socket, user))
            thread.start()

class Room:
    def __init__(self, name):
        self.name = name
        self.clients = []

if __name__ == "__main__":
    rooms = {}
    clients = {}
    start_server()
