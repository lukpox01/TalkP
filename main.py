import curses.textpad
import logging
import socket
import threading
from curses import *


class Chat:
    def __init__(self, client_socket, stdscr, room_name):
        self.stdscr = stdscr
        stdscr.clear()
        self.room_name = room_name
        self.client_socket = client_socket
        self.messages = []
        self.Y, self.X = self.stdscr.getmaxyx()
        self.pad = newpad(self.Y ** 2, self.X - 2)
        self.stdscr.keypad(1)
        self.thread = threading.Thread(target=self.receive_message)
        self.thread.start()

    def show_massages(self):
        self.stdscr.refresh()
        if len(self.messages) > self.Y - 5:
            self.pad.refresh(len(self.messages) - (self.Y - 5) * (len(self.messages) // (self.Y - 5)), 0, 1, 1,
                             self.Y - 5, self.X - 2)
        else:
            self.pad.refresh(0, 0, 1, 1, self.Y - 5, self.X - 2)

    def show(self):
        while True:

            self.stdscr.border()
            self.stdscr.addstr(0, 2, self.room_name)

            curses.echo()
            message = ""
            while message == "":
                self.stdscr.hline(self.Y - 3, 1, 0, self.X - 2)
                self.stdscr.addstr(self.Y - 3, 2, "Input:")
                message = self.stdscr.getstr(self.Y - 2, 2, self.X - 4).decode('utf-8').strip()

            self.stdscr.addstr(self.Y - 3, 2, "Input:")
            self.stdscr.hline(self.Y - 3, 1, 0, self.X - 2)
            curses.noecho()
            if message != "!exit":

                self.send_message(message)
            else:
                self.send_message("!EXIT")
                break
            self.stdscr.clear()

    def send_message(self, message):
        self.client_socket.sendall(message.encode('utf-8'))

    def receive_message(self):  # -----------------------------------
        initcolors()
        logger.debug("Received message start")
        while True:
            try:
                room_name = self.client_socket.recv(1024).decode('utf-8')
                message = self.client_socket.recv(1024)
            except ConnectionAbortedError:
                break
            logger.debug(f"{room_name}-{self.room_name}: {message.decode('utf-8')}")
            if message and room_name == self.room_name:
                color, message = message.decode('utf-8')[:2], message.decode('utf-8')[2:]
                username, message = message.split(":", 1)
                logger.debug(message + "**")
                if len(username+message) > self.X - 2:
                    self.messages.append(username+message)
                    self.messages.append(message[self.X - 2:])
                else:
                    self.messages.append(username+message)
                self.pad.addstr(username + ":", color_pair(int(color)))
                self.pad.addstr(message + "\n")

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
    stdscr.hline(stdscr.getmaxyx()[0] // 2 + 4, stdscr.getmaxyx()[1] // 2 - 10," ", 20)
    curses.noecho()
    return username


def get_room_name(stdscr, to):
    while True:
        curses.echo()
        stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 3, stdscr.getmaxyx()[1] // 2 - 10, f"Enter room name {to}: ")
        roomname = stdscr.getstr(stdscr.getmaxyx()[0] // 2 + 4, stdscr.getmaxyx()[1] // 2 - 10, 30).decode(
            'utf-8').strip()
        curses.noecho()
        if roomname:
            return roomname


def print_menu(stdscr):
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 1, stdscr.getmaxyx()[1] // 2 - 7, "Space - Join main room")
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 3, stdscr.getmaxyx()[1] // 2 - 3, "J - Join room")
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 5, stdscr.getmaxyx()[1] // 2 - 3, "C - Create room")
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 7, stdscr.getmaxyx()[1] // 2 - 3, "S - Settings")
    stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 9, stdscr.getmaxyx()[1] // 2 - 3, "Q - Quit")


def initcolors():
    init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    init_pair(3, curses.COLOR_WHITE, 0)

    init_pair(12, curses.COLOR_RED, curses.COLOR_GREEN)
    init_pair(13, curses.COLOR_RED, curses.COLOR_BLUE)
    init_pair(14, curses.COLOR_RED, curses.COLOR_YELLOW)
    init_pair(15, curses.COLOR_RED, curses.COLOR_CYAN)
    init_pair(16, curses.COLOR_RED, curses.COLOR_MAGENTA)
    init_pair(17, curses.COLOR_RED, curses.COLOR_WHITE)
    init_pair(18, curses.COLOR_RED, curses.COLOR_BLACK)
    init_pair(19, curses.COLOR_RED, 0)

    init_pair(21, curses.COLOR_GREEN, curses.COLOR_RED)
    init_pair(23, curses.COLOR_GREEN, curses.COLOR_BLUE)
    init_pair(24, curses.COLOR_GREEN, curses.COLOR_YELLOW)
    init_pair(25, curses.COLOR_GREEN, curses.COLOR_CYAN)
    init_pair(26, curses.COLOR_GREEN, curses.COLOR_MAGENTA)
    init_pair(27, curses.COLOR_GREEN, curses.COLOR_WHITE)
    init_pair(28, curses.COLOR_GREEN, curses.COLOR_BLACK)
    init_pair(29, curses.COLOR_GREEN, 0)

    init_pair(31, curses.COLOR_BLUE, curses.COLOR_RED)
    init_pair(32, curses.COLOR_BLUE, curses.COLOR_GREEN)
    init_pair(34, curses.COLOR_BLUE, curses.COLOR_YELLOW)
    init_pair(35, curses.COLOR_BLUE, curses.COLOR_CYAN)
    init_pair(36, curses.COLOR_BLUE, curses.COLOR_MAGENTA)
    init_pair(37, curses.COLOR_BLUE, curses.COLOR_WHITE)
    init_pair(38, curses.COLOR_BLUE, curses.COLOR_BLACK)
    init_pair(39, curses.COLOR_BLUE, 0)

    init_pair(41, curses.COLOR_YELLOW, curses.COLOR_RED)
    init_pair(42, curses.COLOR_YELLOW, curses.COLOR_GREEN)
    init_pair(43, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    init_pair(45, curses.COLOR_YELLOW, curses.COLOR_CYAN)
    init_pair(46, curses.COLOR_YELLOW, curses.COLOR_MAGENTA)
    init_pair(47, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    init_pair(48, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    init_pair(49, curses.COLOR_YELLOW, 0)

    init_pair(51, curses.COLOR_CYAN, curses.COLOR_RED)
    init_pair(52, curses.COLOR_CYAN, curses.COLOR_GREEN)
    init_pair(53, curses.COLOR_CYAN, curses.COLOR_BLUE)
    init_pair(54, curses.COLOR_CYAN, curses.COLOR_YELLOW)
    init_pair(56, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
    init_pair(57, curses.COLOR_CYAN, curses.COLOR_WHITE)
    init_pair(58, curses.COLOR_CYAN, curses.COLOR_BLACK)
    init_pair(59, curses.COLOR_CYAN, 0)

    init_pair(61, curses.COLOR_MAGENTA, curses.COLOR_RED)
    init_pair(62, curses.COLOR_MAGENTA, curses.COLOR_GREEN)
    init_pair(63, curses.COLOR_MAGENTA, curses.COLOR_BLUE)
    init_pair(64, curses.COLOR_MAGENTA, curses.COLOR_YELLOW)
    init_pair(65, curses.COLOR_MAGENTA, curses.COLOR_CYAN)
    init_pair(67, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
    init_pair(68, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    init_pair(69, curses.COLOR_MAGENTA, 0)

    init_pair(71, curses.COLOR_WHITE, curses.COLOR_RED)
    init_pair(72, curses.COLOR_WHITE, curses.COLOR_GREEN)
    init_pair(73, curses.COLOR_WHITE, curses.COLOR_BLUE)
    init_pair(74, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    init_pair(75, curses.COLOR_WHITE, curses.COLOR_CYAN)
    init_pair(76, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    init_pair(78, curses.COLOR_WHITE, curses.COLOR_BLACK)
    init_pair(79, curses.COLOR_WHITE, 0)

    init_pair(81, curses.COLOR_BLACK, curses.COLOR_RED)
    init_pair(82, curses.COLOR_BLACK, curses.COLOR_GREEN)
    init_pair(83, curses.COLOR_BLACK, curses.COLOR_BLUE)
    init_pair(84, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    init_pair(85, curses.COLOR_BLACK, curses.COLOR_CYAN)
    init_pair(86, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    init_pair(87, curses.COLOR_BLACK, curses.COLOR_WHITE)
    init_pair(89, curses.COLOR_BLACK, 0)

    init_pair(91, 0, curses.COLOR_RED)
    init_pair(92, 0, curses.COLOR_GREEN)
    init_pair(93, 0, curses.COLOR_BLUE)
    init_pair(94, 0, curses.COLOR_YELLOW)
    init_pair(95, 0, curses.COLOR_CYAN)
    init_pair(96, 0, curses.COLOR_MAGENTA)
    init_pair(97, 0, curses.COLOR_WHITE)
    init_pair(98, 0, curses.COLOR_BLACK)


def print_settings(stdscr, username):
    initcolors()
    last_highlight = [7, 9]
    highlight = [7, 9]
    while True:
        stdscr.addstr(stdscr.getmaxyx()[0] // 2 - 15, stdscr.getmaxyx()[1] // 2 - 38,
                      "Choose color to display your username:")
        stdscr.addstr(stdscr.getmaxyx()[0] // 2 - 15, stdscr.getmaxyx()[1] // 2 + 2,
                      username, curses.color_pair(int(''.join([str(i) for i in highlight]))))
        fore = ["1 - Red", "2 - Green", "3 - Blue", "4 - Yellow", "5 - Cyan", "6 - Magenta", "7 - White", "8 - Black",
                "9 - None"]
        for i, color in enumerate(fore):
            if highlight[0] - 1 == i:
                stdscr.addstr(stdscr.getmaxyx()[0] // 2 - (10 - i), stdscr.getmaxyx()[1] // 2, color, curses.A_REVERSE)
            else:
                stdscr.addstr(stdscr.getmaxyx()[0] // 2 - (10 - i), stdscr.getmaxyx()[1] // 2, color)

        back = ["A - Red", "B - Green", "C - Blue", "D - Yellow", "E - Cyan", "F - Magenta", "G - White", "H - Black",
                "I - None"]
        for i, color in enumerate(back):
            if highlight[1] - 1 == i:
                stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 2 + i, stdscr.getmaxyx()[1] // 2, color, curses.A_REVERSE)
            else:
                stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 2 + i, stdscr.getmaxyx()[1] // 2, color)

        stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 11, stdscr.getmaxyx()[1] // 2 - 3, "Press Q to exit")

        ch = stdscr.getch()
        match ch:
            case 49 | 50 | 51 | 52 | 53 | 54 | 55 | 56 | 57:
                highlight[0] = ch - 48
                if highlight[0] == highlight[1]:
                    highlight[0] = last_highlight[0]
            case 65 | 66 | 67 | 68 | 69 | 70 | 71 | 72 | 73:
                highlight[1] = ch - 64
                if highlight[0] == highlight[1]:
                    highlight[1] = last_highlight[1]
            case 97 | 98 | 99 | 100 | 101 | 102 | 103 | 104 | 105:
                highlight[1] = ch - 96
                if highlight[0] == highlight[1]:
                    highlight[1] = last_highlight[1]
            case 113 | 81:
                return ''.join([str(i) for i in highlight])

        last_highlight[0] = highlight[0]
        last_highlight[1] = highlight[1]


def main(stdscr):
    initcolors()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, 0)
    logger.debug("Start main")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('139.162.137.189', 8888))

    while True:
        print_logo(stdscr)
        username = get_username(stdscr)
        if not username:
            continue
        client_socket.sendall(username.encode('utf-8'))
        username_exists = client_socket.recv(1024).decode('utf-8')
        stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 5, stdscr.getmaxyx()[1] // 2 - 10, username_exists,
                      curses.color_pair(1))
        if username_exists == "false":
            break

    while True:
        stdscr.clear()
        print_logo(stdscr)
        print_menu(stdscr)

        key = stdscr.getch()
        if key == ord('Q') or key == ord('q'):
            client_socket.sendall("_DISCONNECT".encode('utf-8'))
            client_socket.close()
            curses.endwin()
            exit()
        elif key == ord('C') or key == ord('c'):
            logger.debug("Create")
            client_socket.sendall("_CREATE_ROOM".encode('utf-8'))
            stdscr.clear()
            while True:

                print_logo(stdscr)
                roomname = get_room_name(stdscr, "to create")
                client_socket.sendall(roomname.encode('utf-8'))
                ok = client_socket.recv(1024).decode('utf-8')
                stdscr.clear()
                stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 5, stdscr.getmaxyx()[1] // 2 - 10, ok, curses.color_pair(1))
                if ok == "false":
                    break
            c = Chat(client_socket, stdscr, roomname)
            c.show()
            del c

        elif key == ord('J') or key == ord('j'):
            logger.debug("Join")
            client_socket.sendall("_JOIN_ROOM".encode('utf-8'))
            stdscr.clear()
            while True:

                print_logo(stdscr)
                roomname = get_room_name(stdscr, "to join")
                client_socket.sendall(roomname.encode('utf-8'))
                ok = client_socket.recv(1024).decode('utf-8')
                stdscr.clear()
                stdscr.addstr(stdscr.getmaxyx()[0] // 2 + 5, stdscr.getmaxyx()[1] // 2 - 10, ok, curses.color_pair(1))
                if ok == "false":
                    break

            c = Chat(client_socket, stdscr, roomname)
            c.show()
            del c

        elif key == ord('S') or key == ord('s'):
            logger.debug("Settings")
            client_socket.sendall("_SETTINGS".encode('utf-8'))
            stdscr.clear()
            name_colour = print_settings(stdscr, username)
            client_socket.sendall(name_colour.encode('utf-8'))


        elif key == ord(' '):
            logger.debug("SPACE")
            client_socket.sendall("_JOIN_MAIN".encode('utf-8'))
            c = Chat(client_socket, stdscr, "_main_")
            c.show()
            del c


logging.basicConfig(filename="client.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
wrapper(main)
