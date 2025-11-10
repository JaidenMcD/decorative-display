import pygame
from config import *

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True
screen.fill(BACKGROUND_COLOR)
clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.SysFont('Arial', 30) # Font name and size


while running:
    pygame.display.update()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, TEXT_COLOR, pygame.Rect(0, 0, 100, 100), 0)
    
    font.render('Hello Pygame!', True, TEXT_COLOR) # Text, antialias, color (white)


    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(5)  # limits FPS to 60

pygame.quit()