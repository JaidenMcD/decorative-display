import pygame

class UIElement:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        raise NotImplementedError