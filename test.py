#! /usr/bin/python

import os
import pygame
import time

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
lcd = pygame.display.set_mode((480, 320))
lcd.fill((255, 0, 0))
pygame.display.update()
time.sleep(1)
lcd.fill((0, 255, 0))
pygame.display.update()
time.sleep(1)
lcd.fill((0, 0, 255))
pygame.display.update()
time.sleep(1)