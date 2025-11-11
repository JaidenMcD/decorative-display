import pygame, os
from config import *
from ptv_api import get_tram_departures, get_train_departures
from ptv_api import TramStop
import time 

pygame.init()
pygame.mouse.set_visible(False)


screen = pygame.display.set_mode(SCREEN_RES)

update_interval = 10 # seconds
last_update = 0

# Font setup
font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/PressStart2P-Regular.ttf")
font_large = pygame.font.Font(font_path, 24)
font_small = pygame.font.Font(font_path, 16)

clock = pygame.time.Clock()
running = True

screen.fill(BACKGROUND_COLOR)

tramStop = TramStop(os.getenv("TRAM_STOP_ID"))
tramStop.populate_stop()


while running:
    screen.fill(BACKGROUND_COLOR)

    # check if its time to update departures
    current_time = time.time()
    if current_time - last_update >= update_interval:
        tramStop.get_departures()
        last_update = current_time

    # draw UI
    tramStop.display_departures()
    screen.blit(font_large.render("NEXT TRAM", True, TEXT_COLOR), (140, 40))
    screen.blit(font_large.render("NEXT TRAIN", True, TEXT_COLOR), (180, 120))

    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()