import os, time, pygame
from core.config import *
from core.display import create_fonts, clear_screen
from core.ptv_api import TramStop
from datetime import datetime
import pytz

def departures_screen_loop(screen, tz):
    font_large, font_small, font_xsmall = create_fonts()

    tramStop = TramStop(os.getenv("TRAM_STOP_ID"))
    tramStop.populate_stop()

    last_update = 0
    running = True
    clock = pygame.time.Clock()

    while running:
        clear_screen(screen)
        current_time = time.time()
        if current_time - last_update >= UPDATE_INTERVAL:
            tramStop.get_departures()
            last_update = current_time

        departures = tramStop.return_departures()
        screen.blit(font_large.render("NEXT TRAM", True, TEXT_COLOR), (133, 20))

        # city-bound
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
                mins, secs = times[1].split(':')
                screen.blit(font_xsmall.render(f"{mins} m {secs} s", True, TEXT_COLOR), (369,106))
        else:
            screen.blit(font_small.render("No city trams", True, TEXT_COLOR), (307,81))

        # outbound
        start_y, spacing = 81, 40
        for i, dep in enumerate(outbound_deps):
            y = start_y + i * spacing
            screen.blit(font_small.render(f"{dep['route_number']}", True, TEXT_COLOR), (10, y))
            times = dep["countdowns"]
            if len(times) > 0:
                mins, secs = times[0].split(':')
                display_text = "now" if times[0] == "00:00" else f"{int(mins)} m {int(secs)} s"
                screen.blit(font_small.render(display_text, True, TEXT_COLOR), (80, y))
            if len(times) > 1:
                screen.blit(font_xsmall.render(times[1], True, TEXT_COLOR), (125, y + 20))

        pygame.display.flip()
        clock.tick(FPS)

        # touch or key to change display
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return "weather"