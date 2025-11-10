import pygame
from config import *

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True
screen.fill(BACKGROUND_COLOR)
clock = pygame.time.Clock()

while running:
    pygame.display.update()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, 100, 100), 0)
    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(5)  # limits FPS to 60

pygame.quit()