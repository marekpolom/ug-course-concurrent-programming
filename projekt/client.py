from pydoc import cli
import numpy as np
import random, pickle


class GameData:
    def __init__(self):
        self.players = []
        self.max_players = 2

        self.turn = None
        self.first_player = None

        self.draw_player()

    def client_dc(self, address):
        players = list(filter(lambda p: p.address != address, self.players))
        self.players = players
        self.draw_player()

    def client_conn(self, connection, address):
        if len(self.players) == self.max_players:
            return None

        self.players.append(Client(connection, address[0], address[1]))
        return True

    def get_client(self, address):
        player = list(filter(lambda p: p.address == address, self.players))

        if len(player) == 0:
            return None

        return player[0]

    def get_enemy(self, address):
        if len(self.players) > 1:
            return list(filter(lambda p: p.address != address, self.players))[0]

        return None

    def draw_player(self):
        self.turn = random.randint(0, self.max_players - 1)
        self.first_player = self.turn

    def get_player_index(self, client):
        return self.players.index(client)


class Client:
    def __init__(self, connection, ip, port):
        self.connection = connection
        self.ip = ip
        self.port = port

        self.moves_history = []

        self.address = (ip, port)

        self.board = None

    def set_board(self, board_data):
        self.board = np.array([Field(field["hit"], field["ship_id"]) for field in board_data]).reshape(10, 10)

    def clear_board(self):
        self.board = None

    def make_move(self, move):
        field = self.board[move[0]][move[1]]
        field.hit = True

        if self.is_hit(move) and self.is_ship_destroyed(move):
            return {"msg": "You have destroyed the enemy ship!", "ship_id": field.ship_id, "destroyed": True}

        if self.is_hit(move) and field.ship_id is not None:
            return {"msg": "You have hit the enemy ship!", "ship_id": field.ship_id, "destroyed": False}

        return {"msg": "You missed!", "ship_id": field.ship_id, "ship_id": field.ship_id, "destroyed": False}

    def append_history(self, move, ship_id, destroyed):
        self.moves_history.append({"move": move, "ship_id": ship_id, "destroyed": destroyed})

    def get_latest_move(self):
        return self.moves_history[-1]

    def is_defeated(self):
        return len([field for row in self.board for field in row if field.ship_id is not None and not field.hit]) == 0

    def is_hit(self, move):
        return self.board[move[0]][move[1]].ship_id is not None

    def is_ship_destroyed(self, move):
        field = self.board[move[0]][move[1]]

        not_hit_fields = [f for row in self.board for f in row if not f.hit and f.ship_id == field.ship_id]

        return len(not_hit_fields) == 0


class Field:
    def __init__(self, hit, ship_id):
        self.hit = hit
        self.ship_id = ship_id


class Reply:
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def parse_reply(self):
        return pickle.dumps({"type": self.type, "data": self.data})

    @staticmethod
    def reply(game_data, client, action):
        enemy = game_data.get_enemy(client.address)

        if enemy is None:
            return Reply("enemy_dc", {"msg": "Enemy disconected!"})

        return action(game_data, client)

    @staticmethod
    def enemy_dc(client):
        client.clear_board()
        client.moves_history = []

        return Reply("enemy_dc", {"msg": "Enemy disconected!"})

    @staticmethod
    def start_game(client, msg):
        client.set_board(msg["data"]["board"])

        return Reply("wait_for_enemy_join", {"msg": "Waiting for enemy to join!"})

    @staticmethod
    def wait_for_enemy_join(game_data, client):
        enemy = game_data.get_enemy(client.address)

        while enemy is None:
            enemy = game_data.get_enemy(client.address)

        return Reply("wait_for_enemy_start", {"msg": "Waiting for enemy to start a game!"})

    @staticmethod
    def wait_for_enemy_start(game_data, client):
        enemy = game_data.get_enemy(client.address)

        while enemy is not None:
            if enemy.board is not None:
                return Reply("start_game", {"msg": "Game started!"})

            enemy = game_data.get_enemy(client.address)

        return Reply.enemy_dc(client)

    @staticmethod
    def first_player(game_data, client):
        return Reply(
            "turn",
            {
                "msg": "Your turn!" if game_data.players[game_data.turn] == client else "Enemy turn!",
                "turn": game_data.players[game_data.turn] == client,
            },
        )

    @staticmethod
    def wait_for_enemy_move(game_data, client):
        enemy = game_data.get_enemy(client.address)

        if enemy is None:
            return Reply.enemy_dc(client)

        if game_data.players.index(client) == game_data.first_player:
            if len(client.moves_history) == len(enemy.moves_history):
                latest_move = enemy.get_latest_move()
                return Reply(
                    "turn",
                    {
                        "msg": "Your turn!",
                        "turn": True,
                        "move": latest_move["move"],
                        "ship_id": latest_move["ship_id"],
                        "destroyed": latest_move["destroyed"],
                    },
                )
        else:
            if len(client.moves_history) < len(enemy.moves_history):
                latest_move = enemy.get_latest_move()
                return Reply(
                    "turn",
                    {
                        "msg": "Your turn!",
                        "turn": True,
                        "move": latest_move["move"],
                        "ship_id": latest_move["ship_id"],
                        "destroyed": latest_move["destroyed"],
                    },
                )

        return Reply("turn", {"msg": "Enemy turn!", "turn": False})

    @staticmethod
    def make_move(game_data, client, move):
        enemy = game_data.get_enemy(client.address)

        if enemy is None:
            return Reply.enemy_dc(client)

        msg = enemy.make_move(move)
        client.append_history(move, msg["ship_id"], msg["destroyed"])

        game_data.turn = game_data.get_player_index(enemy)

        return Reply(
            "turn",
            {
                "msg": f'{msg["msg"]} Enemy turn!',
                "turn": False,
                "move": move,
                "ship_id": msg["ship_id"],
                "destroyed": msg["destroyed"],
            },
        )

    @staticmethod
    def check_winner(game_data, client):
        if client.is_defeated():
            return Reply("end_game", {"msg": "You loose!", "winner": False})

        if game_data.get_enemy(client.address) is not None:
            if game_data.get_enemy(client.address).is_defeated():
                return Reply("end_game", {"msg": "You win!", "winner": True})

        return Reply("continue", {"msg": "Continue game"})
