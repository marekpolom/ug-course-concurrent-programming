import pygame, math
from _thread import *


class Button:
    def __init__(self, cords, size, text, action, color, color_hovered = None):
        self.x = cords[0]
        self.y = cords[1]

        self.width = size[0]
        self.height = size[1]

        self.font = pygame.font.SysFont("Arial", math.floor(self.height * 0.5))
        self.text = self.font.render(text, True, "white")

        self.color = color
        self.color_hovered = color if color_hovered is None else color_hovered

        self.action = action

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_hovered if self.is_hovered() else self.color, (self.x, self.y, self.width, self.height))
        surf.blit(self.text, self.text.get_rect(center=(self.get_center()[0], self.get_center()[1])))

    def get_bounding_box(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def is_hovered(self):
        mouse = pygame.mouse.get_pos()

        b_box = self.get_bounding_box()
        return b_box[0] < mouse[0] <= b_box[2] and b_box[1] < mouse[1] <= b_box[3]

    def on_click(self):
        self.action()

    def on_click_threadable(self):
        start_new_thread(self.action, ())

    def get_center(self):
        return (self.x + (self.width / 2), self.y + (self.height / 2))

