import socket, pickle
from client import Reply


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost" # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
                                    # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
                                    # ipv4 address. This feild will be the same for all your clients.
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(4096).decode()

    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:
            self.client.send(data)
            reply = self.client.recv(4096)
            return pickle.loads(reply)
        except socket.error as e:
            return str(e)

    @staticmethod
    def start_game(conn, board):
        msg = Reply("start_game", {"board": board.parse_board()})
        return conn.send(msg.parse_reply())

    @staticmethod
    def wait_for_enemy_join(conn):
        msg = Reply("wait_for_enemy_join", {})
        return conn.send(msg.parse_reply())

    @staticmethod
    def wait_for_enemy_start(conn):
        msg = Reply("wait_for_enemy_start", {})
        return conn.send(msg.parse_reply())
        
    @staticmethod
    def first_player(conn):
        msg = Reply("first_player", {})
        return conn.send(msg.parse_reply())

    @staticmethod
    def wait_for_enemy_move(conn):
        msg = Reply("wait_for_enemy_move", {})
        return conn.send(msg.parse_reply())

    @staticmethod
    def make_move(conn, move):
        msg = Reply("move", {"move": move})
        return conn.send(msg.parse_reply())

    @staticmethod
    def check_winner(conn):
        msg = Reply("check_winner", {})
        return conn.send(msg.parse_reply())


class ReplyHandler():
    pass
