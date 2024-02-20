import socket
import threading
from time import sleep


def msg(client_socket, user, room, colour):
    while True:
        message = client_socket.recv(1024)
        if message:

            if message == "!EXIT".encode("utf-8"):
                print("exit")
                while True:
                    client_socket.settimeout(0.5)
                    try:
                        end = client_socket.recv(1024).decode("utf-8")
                    except socket.timeout:
                        end = ""
                    client_socket.settimeout(None)

                    if end == "END":
                        client_socket.sendall("END".encode("utf-8"))
                        break
                    client_socket.sendall("[]".encode("utf-8"))

                print(f"{user} has left the room {room}")
                rooms[room].clients.remove({user: client_socket})

                broadcast(f"{user} has left the room {room}", user, room, colour, )
                break

            print(f"Received message from {user}: {message.decode('utf-8')}")
            broadcast(message.decode('utf-8'), user, room, colour)
        else:
            print(f"{user} has left")
            client_socket.close()
            break

def handle_client(client_socket):
    colour = '79'
    while True:
        user = client_socket.recv(1024).decode('utf-8')
        if user in clients.keys():
            client_socket.sendall("Username already exists".encode('utf-8'))
            print(f"Username {user} already exists")
        else:
            client_socket.sendall("false".encode('utf-8'))
            print("false")
            clients[user] = client_socket
            break



    while True:
        print("Enter instruction: ")

        instruction = client_socket.recv(1024).decode('utf-8')

        if instruction == "_JOIN_MAIN":
            room = "_main_"
            print(instruction)

            rooms[room].clients.append({user: client_socket})
            msg(client_socket, user, room, colour)

        elif instruction == "_CREATE_ROOM":
            while True:
                room = client_socket.recv(1024).decode('utf-8')
                if room in rooms.keys():
                    client_socket.sendall("Room already exists".encode('utf-8'))
                else:
                    print("false-create")
                    client_socket.sendall("false".encode('utf-8'))
                    break
            rooms[room] = Room(room)
            rooms[room].clients.append({user: client_socket})
            print(f"Created room {room}")
            broadcast(f"{user} has joined the room {room}", user, room, colour)
            msg(client_socket, user, room, colour)

        elif instruction == "_JOIN_ROOM":
            while True:
                room = client_socket.recv(1024).decode('utf-8')
                if room in rooms.keys():
                    print("false-join")
                    client_socket.sendall("false".encode('utf-8'))

                    break
                else:
                    client_socket.sendall("Room does not exists".encode('utf-8'))

            rooms[room].clients.append({user: client_socket})
            print(f"Joined room {room}")
            broadcast(f"{user} has joined the room {room}", user, room, colour)
            msg(client_socket, user, room, colour)

        elif instruction == "_SETTINGS":
            colour = client_socket.recv(1024).decode('utf-8')

        elif instruction == "_DISCONNECT":
            print(f"{user} has left")
            clients.pop(user)
            client_socket.close()
            break

def broadcast(message, user, room, colour):
    for client in rooms[room].clients:
        list(client.values())[0].sendall(f"{room}".encode('utf-8'))
        print(f"{room}".encode('utf-8'))
        sleep(0.1)
        list(client.values())[0].sendall(f"{colour}{user}: {message}".encode('utf-8'))
        print(f"{user}: {message}".encode('utf-8'))

def start_server():
    rooms["_main_"] = Room("_main_")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8888))
    server_socket.listen()
    print("Server is listening on port 8888...")

    while True:
        client_socket, client_address = server_socket.accept()

        print(f"Accepted new connection from {client_address[0]}:{client_address[1]}")
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

class Room:
    def __init__(self, name):
        self.name = name
        self.clients = []

if __name__ == "__main__":
    rooms = {}
    clients = {}
    start_server()
