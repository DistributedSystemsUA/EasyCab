import pygame
import threading


LEFT_CLICK = 1
RIGHT_CLICK = 2





def start():
    pygame.init()
    display = pygame.display.set_mode((800,600), pygame.RESIZABLE)

    engine = threading.Thread(target=_start, args=(display,))
    engine.start()
    


def _start(display: pygame.surface.Surface):
    # render ui, map, buttons

    while True:
        event = pygame.event.wait()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT_CLICK:
                # Make square indicator on the map
            elif event.button == RIGHT_CLICK:
                # Send a request to the map
