import pygame, os
from config import *
from ptv_api import MetroStop
import time 
from utils import *
from dotenv import load_dotenv


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

while running:
    screen.fill(BACKGROUND_COLOR)

    # check if its time to update departures
    current_time = time.time()
    if current_time - last_update >= update_interval:
        trainStop.get_departures()
        last_update = current_time

    # draw UI
    

    # Title Card
    screen.blit(font_large.render("Departures", True, TEXT_COLOR), (41,12))
    pygame.draw.rect(screen, TEXT_COLOR, (60,40,200,3))

    # Footer
    pygame.draw.rect(screen, TEXT_COLOR, (60,437,200,3))

    # TRAINS
    departures = trainStop.departures
    inbound = departures[0]
    outbound = departures[1]
    in1 = to_countdown(inbound[0]) if inbound else None
    in2 = to_countdown(inbound[1]) if len(inbound) > 1 else None
    out1 = to_countdown(outbound[0]) if outbound else None
    out2 = to_countdown(outbound[1]) if len(outbound) > 1 else None
    screen.blit(font_small.render("City", True, TEXT_COLOR), (20,62))
    screen.blit(font_small.render(in1, True, TEXT_COLOR), (40,83))
    screen.blit(font_small.render(in2, True, TEXT_COLOR), (40,103))
    screen.blit(font_small.render("Outbound", True, TEXT_COLOR), (20,123))
    screen.blit(font_small.render(out1, True, TEXT_COLOR), (40,143))
    screen.blit(font_small.render(out2, True, TEXT_COLOR), (40,163))


    # City Tram Departures
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (40, 317))
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (40, 337))
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (40, 377))
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (40, 397))
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (210, 317))
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (210, 337))
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (210, 377))
    screen.blit(font_xsmall.render("10 m 64 s", True, TEXT_COLOR), (210, 397))
    screen.blit(font_small.render("5", True, TEXT_COLOR), (153, 323))
    screen.blit(font_small.render("64", True, TEXT_COLOR), (145, 383))

    
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()