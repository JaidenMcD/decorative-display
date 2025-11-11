import pygame, os
from config import *
from ptv_api import get_tram_departures, get_train_departures
from ptv_api import TramStop
import time 

pygame.init()
pygame.mouse.set_visible(False)


screen = pygame.display.set_mode(SCREEN_RES)

update_interval = 30 # seconds
last_update = 0

# Font setup
font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/PressStart2P-Regular.ttf")
font_large = pygame.font.Font(font_path, 24)
font_small = pygame.font.Font(font_path, 16)
font_xsmall = pygame.font.Font(font_path, 8)

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
    departures = tramStop.return_departures()
    screen.blit(font_large.render("NEXT TRAM", True, TEXT_COLOR), (133, 20))

    # City Tram Departures
    city_dep = [d for d in departures if d["direction"] == "city"]
    outbound_deps = [d for d in departures if d["direction"] != "city"]
    if city_dep:
        city = city_dep[0]
        times = city["countdowns"]
        if times:
            mins, secs = times[0].split(':')
            display_text = "now" if times[0] == "00:00" else f"{int(mins)} m {int(secs)} s"
            screen.blit(font_small.render(display_text, True, TEXT_COLOR), (307, 81))
            
        if len(times) > 1:
            ftime = times[1].split(':')
            mins = ftime[0]
            secs = ftime[1]
            screen.blit(font_xsmall.render(f'{mins} m {secs} s', True, TEXT_COLOR), (369,106))
    else:
        screen.blit(font_small.render("No city trams", True, TEXT_COLOR), (307,81))
    


    # --- Draw Outbound Directions (Bottom Section) ---
    start_y = 81  # starting Y coordinate
    spacing = 40  # vertical gap between each direction row

    for i, dep in enumerate(outbound_deps):
        y = start_y + i * spacing
        direction_text = f"{dep['route_number']}"
        screen.blit(font_small.render(direction_text, True, TEXT_COLOR), (10, y))

        # Display up to two countdowns aligned to the right
        times = dep["countdowns"]
        if len(times) > 0:
            mins, secs = times[0].split(':')
            display_text = "now" if times[0] == "00:00" else f"{int(mins)} m {int(secs)} s"
            screen.blit(font_small.render(display_text, True, TEXT_COLOR), (80, y))
        if len(times) > 1:
            mins, secs = times[1].split(':')
            display_text = "now" if times[0] == "00:00" else f"{int(mins)} m {int(secs)} s"
            screen.blit(font_xsmall.render(times[1], True, TEXT_COLOR), (125, y + 20))

    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()