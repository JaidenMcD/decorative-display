import pygame, pytz, os
from core.config import *
from core.display import init_screen
from screens.departures_screen import departures_screen_loop

# Future: from screens.weather_screen import weather_screen_loop

def main():
    tz = pytz.timezone(os.getenv("TIMEZONE"))
    screen = init_screen()
    current_screen = "tram"

    while True:
        if current_screen == "tram":
            next_screen = departures_screen_loop(screen, tz)
        elif current_screen == "weather":
            # placeholder
            next_screen = "tram"
        else:
            break
        current_screen = next_screen

if __name__ == "__main__":
    main()