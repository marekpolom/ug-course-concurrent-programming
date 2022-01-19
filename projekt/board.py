import pygame, random
import numpy as np
from _thread import *


class Board:
    def __init__(self, cords, shape, fields_size, gap, border, colors):
        self.x = cords[0]
        self.y = cords[1]

        self.shape = shape
        self.gap = gap
        self.border = border
        self.colors = colors

        self.fields_size = fields_size

        self.width = (2 * self.border) + ((self.shape[0] - 1) * self.gap) + (self.shape[0] * self.fields_size[0])
        self.height = (2 * self.border) + ((self.shape[1] - 1) * self.gap) + (self.shape[1] * self.fields_size[1])

    def draw(self, surf):
        pygame.draw.rect(surf, self.colors["color"], (self.x, self.y, self.width, self.height))

    def get_bounding_box(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def is_hovered(self):
        mouse = pygame.mouse.get_pos()

        b_box = self.get_bounding_box()
        return b_box[0] < mouse[0] <= b_box[2] and b_box[1] < mouse[1] <= b_box[3]

    def get_field_colors(self):
        return {
            "_".join(key.split("_")[1:]): value
            for key, value in zip(self.colors.keys(), self.colors.values())
            if key.split("_")[0] == "field"
        }


class PlayerBoard(Board):
    def __init__(self, cords, shape, fields_size, gap, border, colors):
        super().__init__(cords, shape, fields_size, gap, border, colors)

        self.board = np.arange(self.shape[0] * self.shape[1]).reshape(self.shape)
        self.board = np.array(
            [
                PlayerField(cords, np.where(self.board == i), self.fields_size, self.get_field_colors(), self)
                for i in range(self.shape[0] * self.shape[1])
            ]
        ).reshape(self.shape)

        self.ships = [Ship(id, size, self) for id, size in enumerate([4, 3, 3, 2, 2, 2, 1, 1, 1, 1])]

        self.generated = False

    def draw(self, surf):
        pygame.draw.rect(surf, self.colors["color"], (self.x, self.y, self.width, self.height))

        [field.draw(surf) for row in self.board for field in row]

    def get_field_neighbors(self, field):
        position = (field.positionX, field.positionY)

        return {
            dir: self.board[position[0] + x][position[1] + y]
            for x, y, dir in [
                (0, -1, "U"),
                (1, -1, "UR"),
                (1, 0, "R"),
                (1, 1, "DR"),
                (0, 1, "D"),
                (-1, 1, "DL"),
                (-1, 0, "L"),
                (-1, -1, "UL"),
            ]
            if 0 <= position[0] + x < self.shape[0] and 0 <= position[1] + y < self.shape[1]
        }

    def get_field_neighbors_h_v(self, field):
        neighbors = self.get_field_neighbors(field)

        return {key: neighbors[key] for key in neighbors.keys() if len(key) == 1}

    def get_field_neighbors_diag(self, field):
        neighbors = self.get_field_neighbors(field)

        return {key: neighbors[key] for key in neighbors.keys() if len(key) == 2}

    def select_field(self):
        if self.is_hovered():
            selected = [field.switch_select() for row in self.board for field in row if field.is_hovered()]

            if len(selected) > 0:
                field = selected[0]

                neighbors = self.get_field_neighbors(field)

                pass

    def get_not_selected_fields(self, recursive=False):
        fields = [field for row in self.board for field in row if not field.selected]

        if not recursive:
            return fields

        return [f for f in fields if len([n for n in self.get_field_neighbors(f).values() if n.selected]) == 0]

    def generate_ships_placement(self):
        self.clear_board()
        [ship.generate() for ship in self.ships]
        self.generated = True

    def clear_board(self):
        [field.clear_field() for row in self.board for field in row]
        [ship.clear_ship() for ship in self.ships]
        self.generated = False

    def parse_board(self):
        return [
            {"hit": field.hit, "ship_id": field.parent.id if field.parent is not None else field.parent}
            for row in self.board
            for field in row
        ]

    def destroy_ship(self, id):
        [field.destroy() for field in self.ships[id].fields]
    
    def make_move(self, x, y, ship_id, destroyed):
        field = self.board[x][y]

        field.hit = True
        field.ship_id = ship_id

        if destroyed:
            self.destroy_ship(ship_id)


class EnemyBoard(Board):
    def __init__(self, cords, shape, fields_size, gap, border, colors):
        super().__init__(cords, shape, fields_size, gap, border, colors)

        self.board = None

    def set_board(self):
        temp_board = np.arange(self.shape[0] * self.shape[1]).reshape(self.shape)
        self.board = np.array(
            [
                Field((self.x, self.y), np.where(temp_board == field), self.fields_size, self.get_field_colors(), self)
                for field in range(self.shape[0] * self.shape[1])
            ]
        ).reshape(self.shape)

    def draw(self, surf):
        if self.board is None:
            pygame.draw.rect(surf, self.colors["color_clear"], (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(surf, self.colors["color"], (self.x, self.y, self.width, self.height))
            [field.draw(surf) for row in self.board for field in row]

    def make_move(self, x, y, ship_id, destroyed):
        field = self.board[x][y]

        field.hit = True
        field.ship_id = ship_id

        if destroyed:
            self.destroy_ship(ship_id)

    def on_click(self, action):
        if self.board is not None:
            fields = [field for row in self.board for field in row if field.is_hovered() and not field.hit]

            if len(fields) > 0:
                start_new_thread(action, (fields[0].positionX, fields[0].positionY))

    def clear_board(self):
        self.board = None
    
    def search_for_ship(self, id):
        return [field for row in self.board for field in row if field.ship_id == id]

    def destroy_ship(self, id):
        [field.destroy() for field in self.search_for_ship(id)]

class Field:
    def __init__(self, cords, position, size, colors, board):
        self.colors = colors
        self.width = size[0]
        self.height = size[1]

        self.positionX = position[0][0]
        self.positionY = position[1][0]

        self.x = (self.positionX * (board.gap + self.width)) + board.border + cords[0]
        self.y = (self.positionY * (board.gap + self.height)) + board.border + cords[1]

        self.selected = False
        self.ship_id = None
        self.destroyed = False
        self.hit = False

    def draw(self, surf):
        pygame.draw.rect(
            surf,
            self.get_color(),
            (self.x, self.y, self.width, self.height),
        )

    def get_color(self):
        if self.hit and self.ship_id is not None and self.destroyed:
            if self.is_hovered():
                return self.colors["color_destroyed_hover"]
            
            return self.colors["color_destroyed"]

        if self.hit and self.ship_id is not None and not self.destroyed:
            if self.is_hovered():
                return self.colors["color_hit_hover"]
            
            return self.colors["color_hit"]

        if self.hit and self.ship_id is None:
            if self.is_hovered():
                return self.colors["color_missed_hover"]

            return self.colors["color_missed"]

        if self.is_hovered() or self.selected:
            return self.colors["color_default_hover"]

        return self.colors["color_default"]

    def is_hovered(self):
        mouse = pygame.mouse.get_pos()

        b_box = self.get_bounding_box()
        return b_box[0] < mouse[0] <= b_box[2] and b_box[1] < mouse[1] <= b_box[3]

    def get_bounding_box(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def switch_select(self):
        self.selected = False if self.selected else True

    def destroy(self):
        self.destroyed = True


class PlayerField(Field):
    def __init__(self, cords, position, size, colors, board):
        super().__init__(cords, position, size, colors, board)
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    def clear_field(self):
        self.hit = False
        self.selected = None
        self.parent = None


class Ship:
    def __init__(self, id, size, board):
        self.id = id
        self.size = size
        self.fields = []

        self.parent = board

    def is_full(self):
        return self.size == len(self.fields)

    def generate(self):
        self.clear_ship()
        avaible_fields = self.parent.get_not_selected_fields(True)

        fields = []

        while True:
            fields = [avaible_fields[random.randint(0, len(avaible_fields) - 1)]]

            direction = list(self.parent.get_field_neighbors_h_v(fields[0]).keys())[
                random.randint(0, len(self.parent.get_field_neighbors_h_v(fields[0]).keys()) - 1)
            ]

            for i in range(self.size - 1):
                neighbors = self.parent.get_field_neighbors_h_v(fields[i])

                if not direction in neighbors.keys():
                    break

                if (
                    len([n for n in list(self.parent.get_field_neighbors(neighbors[direction]).values()) if n.selected])
                    > 0
                ):
                    break

                fields.append(neighbors[direction])

            if len(fields) == self.size:
                break

        [(f.switch_select(), f.set_parent(self)) for f in fields]

        self.fields = fields

    def clear_ship(self):
        [field.clear_field() for field in self.fields]
        self.fields = []

    def is_destroyed(self):
        return len([field for field in self.fields if field.hit]) == self.size
