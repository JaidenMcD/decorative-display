import pygame

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((480, 320))
running = True
screen.fill((255, 255, 255))
clock = pygame.time.Clock()

while running:
    pygame.display.update()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(5)  # limits FPS to 60

pygame.quit()