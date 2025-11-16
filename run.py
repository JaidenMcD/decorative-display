import pygame, os
from config import *
from ptv_api import MetroStop, TramStop
import time 
from utils import *
from dotenv import load_dotenv
from ui.departure_card import DepartureCard


print("begin")
load_dotenv()
print("env file loaded")
device = int(os.getenv("DEVICE"))
print(f"device = {device}")

if device == 1:
    print('setting enviroment variables')
    os.environ["DISPLAY"] = ":0"
    os.environ["SDL_FBDEV"] = "/dev/fb1"
    os.environ["SDL_VIDEODRIVER"] = "fbcon"
    os.environ["SDL_NOMOUSE"] = "1" 

pygame.init()
pygame.mouse.set_visible(False)

if device == 1:
    screen = pygame.display.set_mode(SCREEN_RES, pygame.FULLSCREEN | pygame.NOFRAME)
else:
    screen = pygame.display.set_mode(SCREEN_RES)

update_interval = 5 # seconds
last_update = 0

# Font setup
font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/PressStart2P-Regular.ttf")
font_large = pygame.font.Font(font_path, 24)
font_small = pygame.font.Font(font_path, 16)
font_xsmall = pygame.font.Font(font_path, 8)

clock = pygame.time.Clock()
running = True

print('starting up')
screen.fill(BACKGROUND_COLOR)
time.sleep(1)
screen.fill(TEXT_COLOR)
time.sleep(1)
screen.fill(BACKGROUND_COLOR)



trainStop = MetroStop(os.getenv("TRAIN_STOP_ID"))
tramStop = TramStop(os.getenv("TRAM_STOP_ID"))

# Define UI elements
train_city = DepartureCard(10, 62, 'City', font_small, TEXT_COLOR)
train_out = DepartureCard(10,123,'Outbound', font_small, TEXT_COLOR)

while running:
    screen.fill(BACKGROUND_COLOR)

    # check if its time to update departures
    current_time = time.time()
    if current_time - last_update >= update_interval:
        trainStop.get_departures()
        tramStop.get_departures()
        last_update = current_time

    # draw UI
    

    # Title Card
    screen.blit(font_large.render("Departures", True, TEXT_COLOR), (42,10))
    pygame.draw.rect(screen, TEXT_COLOR, (60,39,200,3))

    # Footer
    pygame.draw.rect(screen, TEXT_COLOR, (60,437,200,3))

    # TRAINS
    departures = trainStop.departures

    inbound = departures[0]
    in1 = to_countdown(inbound[0]) if inbound else None
    in2 = to_countdown(inbound[1]) if len(inbound) > 1 else None
    train_city.update_times([in1, in2])
    train_city.draw(screen)

    outbound = departures[1]
    out1 = to_countdown(outbound[0]) if outbound else None
    out2 = to_countdown(outbound[1]) if len(outbound) > 1 else None
    train_out.update_times([out1, out2])
    train_out.draw(screen)



    # --- Tram Departures (2 routes, 2 inbound + 2 outbound each) ---

    tram_routes = tramStop.routes  # {route_number: {"inbound": [...], "outbound": [...]}}

    # Sort route numbers so e.g. "5" appears above "64"
    route_numbers = sorted(tram_routes.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))

    # Layout config: one row per route
    # Row 0 ~ your old '5' row, Row 1 ~ your old '64' row
    row_configs = [
        {"y_base": 317, "label_x": 153, "label_y": 323},  # first route
        {"y_base": 377, "label_x": 145, "label_y": 383},  # second route
    ]

    inbound_x = 40
    outbound_x = 210
    line_spacing = 20  # vertical spacing between the two times in each column

    for idx, route_number in enumerate(route_numbers[:len(row_configs)]):
        cfg = row_configs[idx]
        entry = tram_routes[route_number]
        inbound = entry.get("inbound", [])
        outbound = entry.get("outbound", [])

        # Convert datetimes to countdown strings
        in1 = to_countdown(inbound[0]) if len(inbound) > 0 else None
        in2 = to_countdown(inbound[1]) if len(inbound) > 1 else None
        out1 = to_countdown(outbound[0]) if len(outbound) > 0 else None
        out2 = to_countdown(outbound[1]) if len(outbound) > 1 else None

        y0 = cfg["y_base"]

        # Inbound column
        if in1:
            screen.blit(font_xsmall.render(in1, True, TEXT_COLOR), (inbound_x, y0))
        if in2:
            screen.blit(font_xsmall.render(in2, True, TEXT_COLOR), (inbound_x, y0 + line_spacing))

        # Outbound column
        if out1:
            screen.blit(font_xsmall.render(out1, True, TEXT_COLOR), (outbound_x, y0))
        if out2:
            screen.blit(font_xsmall.render(out2, True, TEXT_COLOR), (outbound_x, y0 + line_spacing))

        # Route number label in the middle
        screen.blit(font_small.render(str(route_number), True, TEXT_COLOR),
                    (cfg["label_x"], cfg["label_y"]))

    
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()