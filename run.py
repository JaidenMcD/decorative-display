import pygame
from config import *

pygame.init()
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode(SCREEN_RES)
canvas = pygame.Surface(BASE_RES)  # low-res drawing surface

running = True
screen.fill(BACKGROUND_COLOR)


font = pygame.font.Font(None, 16)  # small pixel font
text = font.render("NEXT TRAIN", True, TEXT_COLOR)

clock = pygame.time.Clock()

while running:
    # --- draw at low res ---
    canvas.fill(BACKGROUND_COLOR)
    canvas.blit(text, (20, 10))
    pygame.draw.rect(canvas, TEXT_COLOR, (50, 40, 20, 10))  # sample shape

    # --- scale up to screen ---
    scaled = pygame.transform.scale(canvas, SCREEN_RES)
    screen.blit(scaled, (0,0))
    pygame.display.flip()
    clock.tick(5)

pygame.quit()