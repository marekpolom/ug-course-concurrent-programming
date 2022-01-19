import pygame, time, pickle
from network import Network
from board import PlayerBoard, EnemyBoard
from interface import Button
from _thread import *

game_started = False
global_game_data = None


class Game:
    def __init__(self, w, h):
        pygame.font.init()

        self.net = Network()
        self.width = w
        self.height = h
        self.font = pygame.font.SysFont("Arial", 18)
        self.board = PlayerBoard(
            (62, 62),
            (10, 10),
            (30, 30),
            2,
            4,
            {
                "color": "gray",
                "field_color_default": "red",
                "field_color_default_hover": "green",
                "field_color_destroyed": "magenta",
                "field_color_destroyed_hover": "cyan",
                "field_color_hit": "black",
                "field_color_hit_hover": "purple",
                "field_color_missed": "yellow",
                "field_color_missed_hover": "blue",
            },
        )
        self.enemy_board = EnemyBoard(
            (62, 512),
            (10, 10),
            (30, 30),
            2,
            4,
            {
                "color": "gray",
                "color_clear": "gray",
                "field_color_default": "red",
                "field_color_default_hover": "green",
                "field_color_destroyed": "magenta",
                "field_color_destroyed_hover": "cyan",
                "field_color_hit": "black",
                "field_color_hit_hover": "purple",
                "field_color_missed": "yellow",
                "field_color_missed_hover": "blue",
            },
        )
        self.buttons = [
            Button((62, 430), (100, 40), "Generuj", self.board.generate_ships_placement, "blue", "yellow"),
            Button((175, 430), (100, 40), "Wyczyść", self.board.clear_board, "blue", "yellow"),
        ]
        self.threadable_buttons = [
            Button((288, 430), (100, 40), "Start", self.start_game, "blue", "yellow"),
        ]
        self.canvas = Canvas(self.width, self.height, "Statki")

        self.clickable = []

    def run(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False

                if event.type == pygame.MOUSEBUTTONUP:
                    # self.board.select_field()
                    if not game_started:
                        [button.on_click() for button in self.buttons if button.is_hovered()]
                        if self.board.generated:
                            [button.on_click_threadable() for button in self.threadable_buttons if button.is_hovered()]
                    # [clickable.on_click() for clickable in self.clickable if clickable.is_hovered()]
                    if game_started and global_game_data["type"] != "end_game":
                        self.enemy_board.on_click(self.make_move)

            keys = pygame.key.get_pressed()

            # Update Canvas
            self.canvas.draw_background()

            self.board.draw(self.canvas.get_canvas())
            self.enemy_board.draw(self.canvas.get_canvas())

            if not game_started:
                [button.draw(self.canvas.get_canvas()) for button in self.buttons]

                if self.board.generated:
                    [button.draw(self.canvas.get_canvas()) for button in self.threadable_buttons]

            if game_started:
                pygame.draw.rect(self.canvas.get_canvas(), "green", (5, 5, 20, 20))

            if global_game_data is not None:
                text = self.font.render(global_game_data["data"]["msg"], True, "black")
                self.canvas.get_canvas().blit(text, text.get_rect(center=(225, 31)))

            self.canvas.update()

        pygame.quit()

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(self.player.x) + "," + str(self.player.y)
        reply = self.net.send(data)
        return reply

    def start_game(self):
        global global_game_data, game_started

        if self.board.generated and not game_started:
            global_game_data = Network.start_game(self.net, self.board)
            game_started = True

            print(global_game_data)

            if global_game_data["type"] == "wait_for_enemy_join":
                global_game_data = Network.wait_for_enemy_join(self.net)

            print(global_game_data)

            if global_game_data["type"] == "wait_for_enemy_start":
                global_game_data = Network.wait_for_enemy_start(self.net)

            print(global_game_data)

            if global_game_data["type"] == "enemy_dc":
                # TODO
                # DO SOMETHING!!
                self.enemy_dc()
                return

            print(global_game_data)

            if global_game_data["type"] == "start_game":
                self.enemy_board.set_board()

                global_game_data = Network.first_player(self.net)

            print(global_game_data)

            time.sleep(3)

            while True:
                if global_game_data["type"] == "enemy_dc":
                    break

                if global_game_data["type"] == "turn":
                    if not global_game_data["data"]["turn"]:
                        time.sleep(0.5)
                        global_game_data = Network.wait_for_enemy_move(self.net)
                    else:
                        break

            if global_game_data["type"] == "enemy_dc":
                # TODO
                # DO SOMETHING!!
                self.enemy_dc()
                return

            if global_game_data["type"] == "turn":
                move = global_game_data["data"]["move"]
                ship_id = global_game_data["data"]["ship_id"]
                destroyed = global_game_data["data"]["destroyed"]
                self.board.make_move(move[0], move[1], ship_id, destroyed)

                reply = Network.check_winner(self.net)

                if reply["type"] == "end_game":
                    game_started = False
                    global_game_data = reply

    def make_move(self, x, y):
        global global_game_data, game_started

        if game_started and global_game_data["type"] == "turn":
            if global_game_data["data"]["turn"]:
                global_game_data = Network.make_move(self.net, (x, y))

                if global_game_data["type"] == "enemy_dc":
                    # TODO
                    # DO SOMETHING!!
                    self.enemy_dc()
                    return

                print(global_game_data)

                move = global_game_data["data"]["move"]
                ship_id = global_game_data["data"]["ship_id"]
                destroyed = global_game_data["data"]["destroyed"]
                self.enemy_board.make_move(move[0], move[1], ship_id, destroyed)

                reply = Network.check_winner(self.net)

                print(reply)

                if reply["type"] == "end_game":
                    game_started = False
                    global_game_data = reply
                    return

                while True:
                    if global_game_data["type"] == "enemy_dc":
                        break

                    if global_game_data["type"] == "turn":
                        if not global_game_data["data"]["turn"]:
                            time.sleep(1)
                            global_game_data = Network.wait_for_enemy_move(self.net)
                        else:
                            break

                print(global_game_data)

                if global_game_data["type"] == "enemy_dc":
                    # TODO
                    # DO SOMETHING!!
                    self.enemy_dc()
                    return

                move = global_game_data["data"]["move"]
                ship_id = global_game_data["data"]["ship_id"]
                destroyed = global_game_data["data"]["destroyed"]
                self.board.make_move(move[0], move[1], ship_id, destroyed)

                reply = Network.check_winner(self.net)

                print(reply)

                if reply["type"] == "end_game":
                    game_started = False
                    global_game_data = reply

    def enemy_dc(self):
        global game_started

        game_started = False
        self.enemy_board.clear_board()
        self.board.clear_board()

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1])
        except:
            return 0, 0


class Canvas:
    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", size)
        render = font.render(text, 1, (0, 0, 0))

        self.screen.draw(render, (x, y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        self.screen.fill((255, 255, 255))
