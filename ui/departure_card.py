import pygame
from .base import UIElement

class DepartureCard(UIElement):
    """
    Displays something like:
        Title      time1
                   time2
    """
    def __init__(self, x, y, title, font, colour):
        super().__init__(x, y)
        self.title = title
        self.font = font
        self.colour = colour
        self.times = []
    
    def update_times(self, newTimes):
        self.times = newTimes
    
    def draw(self, screen):
        # Title
        screen.blit(self.font.render(self.title, True, self.colour), (self.x, self.y))

        # Values
        i = 0
        for time in self.times:
            screen.blit(self.font.render(time, True, self.colour), (self.x + 160, self.y + i*30))
            i = i+1