import pygame, os

pygame.init()
pygame.mouse.set_visible(False)

BASE_RES = (120, 80)
SCREEN_RES = (480, 320)
SCALE = SCREEN_RES[0] // BASE_RES[0]

BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode(SCREEN_RES)
canvas = pygame.Surface(BASE_RES)

# Font setup
font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/Px437_IBM_PGC.ttf")
font = pygame.font.Font(font_path, 8)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Draw on low-res canvas ---
    canvas.fill(BACKGROUND_COLOR)
    text = font.render("NEXT TRAIN", False, TEXT_COLOR)
    canvas.blit(text, (10, 5))
    pygame.draw.rect(canvas, TEXT_COLOR, (50, 40, 10, 10))

    # --- Scale up with nearest-neighbor ---
    scaled = pygame.transform.scale_by(canvas, SCALE)
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

    clock.tick(30)

pygame.quit()