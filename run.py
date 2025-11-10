import pygame, os
from config import *

pygame.init()
pygame.mouse.set_visible(False)


screen = pygame.display.set_mode(SCREEN_RES)

# Font setup
font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/PressStart2P-Regular.ttf")
font_large = pygame.font.Font(None, 24)

clock = pygame.time.Clock()
running = True

screen.fill(BACKGROUND_COLOR)

while running:
    screen.fill(BACKGROUND_COLOR)

    screen.blit(font_large.render("NEXT TRAM", True, TEXT_COLOR), (140, 40))
    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()