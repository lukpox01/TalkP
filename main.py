import curses.textpad
import socket
import threading
from curses import *
import  logging


class Chat:
    def __init__(self, client_socket, stdscr):
        self.stdscr = stdscr
        stdscr.clear()
        self.client_socket = client_socket
        self.messages = []
        self.Y, self.X = self.stdscr.getmaxyx()
        self.pad = newpad(self.Y**3, self.X - 2)
        self.stdscr.keypad(1)
        thread = threading.Thread(target=self.receive_message)
        thread.start()

    def show_massages(self):
        self.stdscr.refresh()
        if len(self.messages) > self.Y - 5:
            self.pad.refresh(len(self.messages) - (self.Y - 5) * (len(self.messages) // (self.Y - 5))   , 0, 1, 1, self.Y - 5, self.X-2)
        else:
            self.pad.refresh(0, 0, 1, 1, self.Y - 5, self.X-2)

    def show(self):
        while True:
            self.stdscr.border()

            curses.echo()
            message = ""
            while message == "":
                curses.textpad.rectangle(self.stdscr, self.Y - 4, 1, self.Y - 2, self.X - 2)
                message = self.stdscr.getstr(self.Y - 3, 2, self.X - 4).decode('utf-8').strip()

            curses.textpad.rectangle(self.stdscr, self.Y - 4, 1, self.Y - 2, self.X - 2)
            curses.noecho()
            if message != "!exit":

                self.send_message(message)
            else:
                self.send_message("!EXIT")
                break
            self.stdscr.clear()

    def send_message(self, message):
        self.client_socket.sendall(message.encode('utf-8'))

    def receive_message(self):
        room = "_main_" #-----------------------------------
        logger.debug("Received message start")
        while True:
            room_name = self.client_socket.recv(1024).decode('utf-8')
            message = self.client_socket.recv(1024)
            if message and room_name == room:
                self.messages.append(message.decode('utf-8'))
                self.pad.addstr(message.decode('utf-8') + "\n")
                self.show_massages()




logo = ["████████╗███████╗██████╗ ███╗   ███╗████████╗ █████╗ ██╗     ██╗  ██╗",
        "╚══██╔══╝██╔════╝██╔══██╗████╗ ████║╚══██╔══╝██╔══██╗██║     ██║ ██╔╝",
        "   ██║   █████╗  ██████╔╝██╔████╔██║   ██║   ███████║██║     █████╔╝ ",
        "   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║   ██║   ██╔══██║██║     ██╔═██╗ ",
        "   ██║   ███████╗██║  ██║██║ ╚═╝ ██║   ██║   ██║  ██║███████╗██║  ██╗",
        "   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"]


def print_logo(stdscr):
    for y, line in enumerate(logo):
        stdscr.addstr(stdscr.getmaxyx()[0] // 2 - len(logo) // 2 + y - stdscr.getmaxyx()[0] // 2 // 2,
                      stdscr.getmaxyx()[1] // 2 - len(line) // 2, line)


def get_username(stdscr):
    curses.echo()
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 3, stdscr.getmaxyx()[1] // 2 - 10, "Enter username: ")
    username = stdscr.getstr(stdscr.getmaxyx()[0] // 2 + 4, stdscr.getmaxyx()[1] // 2 - 10, 20).decode('utf-8').strip()
    curses.noecho()
    return username


def print_menu(stdscr):
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 1, stdscr.getmaxyx()[1] // 2 - 7, "Space - Join main room")
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 3, stdscr.getmaxyx()[1] // 2 - 3, "J - Join room")
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 5, stdscr.getmaxyx()[1] // 2 - 3, "C - Create room")
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 7, stdscr.getmaxyx()[1] // 2 - 3, "Q - Quit")




def main(stdscr):
    logger.debug("Start main")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    print_logo(stdscr)
    username = get_username(stdscr)
    client_socket.sendall(username.encode('utf-8'))

    while True:
        stdscr.clear()
        print_logo(stdscr)
        print_menu(stdscr)

        key = stdscr.getch()
        if key == ord('Q') or key == ord('q'):
            client_socket.sendall("_DISCONNECT".encode('utf-8'))
            curses.endwin()
        elif key == ord('C') or key == ord('c'):
            pass
        elif key == ord('J') or key == ord('j'):
            pass
        elif key == ord(' '):
            logger.debug("SPACE")
            client_socket.sendall("_JOIN_MAIN".encode('utf-8'))
            c = Chat(client_socket, stdscr)

            c.show()

logging.basicConfig(filename="client.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
wrapper(main)
