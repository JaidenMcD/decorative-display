import pygame
from core.config import *

pygame.init()
pygame.mouse.set_visible(False)

def create_fonts():
    font_large = pygame.font.Font(FONT_PATH, 24)
    font_small = pygame.font.Font(FONT_PATH, 16)
    font_xsmall = pygame.font.Font(FONT_PATH, 8)
    return font_large, font_small, font_xsmall

def init_screen():
    return pygame.display.set_mode(SCREEN_RES)

def clear_screen(screen):
    screen.fill(BACKGROUND_COLOR)