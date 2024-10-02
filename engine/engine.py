import pygame
import threading
from random import randint

from game_map import *


LEFT_CLICK = 1
RIGHT_CLICK = 2

MAP_WIDTH = 20

isRunning: bool = False
gameMap: GameMap = None
#ui: UI = None


def start():
    pygame.init()
    pygame.font.init()

    display = pygame.display.set_mode((800,600), pygame.RESIZABLE)
    gameMap = GameMap(display, MAP_WIDTH, *randEntities(20))
    gameMap.render()
    #TODO: init ui

    engine = threading.Thread(target=_run_thread)
    engine.start()


def _run_thread():
    while True:
        event = pygame.event.wait()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT_CLICK:
                # Make square indicator on the map
                pass
            elif event.button == RIGHT_CLICK:
                # Send a request to the map
                pass
        #TODO: catch pygame resize event
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            engineIsRunning = False
            pygame.font.quit()
            pygame.quit()
            exit()


def randPos(mapSideLength: int):
    return Position(randint(0, mapSideLength -1), randint(0, mapSideLength -1))


def randEntity() -> Entity:
    return Taxi(randPos(MAP_WIDTH), randPos(MAP_WIDTH)) if randint(0,1) == 0 else Client(randPos(MAP_WIDTH), randPos(MAP_WIDTH))


def randEntities(n: int) -> list[Entity]:
    return [randEntity() for _ in range(n)]
