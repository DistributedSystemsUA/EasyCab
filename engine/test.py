import pygame

pygame.init()

surface = pygame.display.set_mode((350,350), pygame.RESIZABLE)
pygame.display.set_caption("Resizable window")

while True:
    surface.fill((0,0,0))
    pygame.draw.rect(surface, (200, 0, 0), (surface.get_width() / 3, surface.get_height() / 3, surface.get_width() / 3, surface.get_height() / 3))

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) :
            pygame.quit()
            exit()
        elif event.type == pygame.VIDEORESIZE :
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
