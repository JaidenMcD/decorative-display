import pygame, os
from config import *
from ptv_api import get_tram_departures, get_train_departures

pygame.init()
pygame.mouse.set_visible(False)


screen = pygame.display.set_mode(SCREEN_RES)

# Font setup
font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/PressStart2P-Regular.ttf")
font_large = pygame.font.Font(font_path, 24)
font_small = pygame.font.Font(font_path, 16)

clock = pygame.time.Clock()
running = True

screen.fill(BACKGROUND_COLOR)

print(get_tram_departures())
print(get_train_departures())

while running:
    screen.fill(BACKGROUND_COLOR)

    screen.blit(font_large.render("NEXT TRAM", True, TEXT_COLOR), (140, 40))
    screen.blit(font_large.render("NEXT TRAIN", True, TEXT_COLOR), (180, 120))
    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()