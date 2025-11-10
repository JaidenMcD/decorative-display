import pygame
from config import *

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True
screen.fill(BACKGROUND_COLOR)
clock = pygame.time.Clock()

font_large = pygame.font.Font(None, 48)

while running:
    pygame.display.update()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(BACKGROUND_COLOR)
    
    screen.blit(font_large.render("NEXT TRAM", True, TEXT_COLOR), (140, 40))



    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(5)  # limits FPS to 60

pygame.quit()