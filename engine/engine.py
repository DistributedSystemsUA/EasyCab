import pygame
import threading
from random import randint
from typing import Callable

from entities import *
from game_map import *


LEFT_CLICK = 1
RIGHT_CLICK = 2

MAP_WIDTH = 20

isRunning: bool = True
pointedEntity: Entity = None
gameMap: GameMap = None
#ui: UI = None


def start(socket_app: Callable):
    global gameMap
    global isRunning
    global pointedEntity

    pygame.init()
    pygame.font.init()

    display = pygame.display.set_mode((800,600), pygame.RESIZABLE)
    gameMap = GameMap(display, MAP_WIDTH)
    #TODO: init ui

    gameMap.addEntities(*randEntities(10)) # TODO: remove this
    gameMap.render()
    pygame.display.flip()

    client_application = threading.Thread(target=socket_app)
    client_application.start()

    while True:
        event = pygame.event.wait()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT_CLICK:
                _processClick(*pygame.mouse.get_pos())
        elif event.type == Taxi.MoveEvent:
            # TODO: update the position on the map's dictionary to overlap (if necessary) with more positions
            # IMPORTANT: always read the last element of the overlapped position list in the dictionary entrance
            # maybe make a function _handleMove
            pass
        # TODO: create an event to make operations with Taxis
        elif event.type == pygame.VIDEORESIZE:
            gameMap.resizeDisplay()
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            _closeApplication()

        gameMap.display.fill("black")
        gameMap.render()
        _drawEntityPointer()
        pygame.display.flip()


def randPos(mapSideLength: int):
    return Position(randint(1, mapSideLength), randint(1, mapSideLength))


def randEntity() -> Entity:
    return Taxi(randPos(MAP_WIDTH), randPos(MAP_WIDTH)) if randint(0,1) == 0 else Client(randPos(MAP_WIDTH), randPos(MAP_WIDTH))


def randEntities(n: int) -> list[Entity]:
    return [randEntity() for _ in range(n)]


#########################################
#          INTERNAL FUNCTIONS           #
#########################################


def _processClick(x, y):
    loc = gameMap.getBoxLoc(x, y)
    if loc is not None:
        pointedEntity = gameMap.locateEntities(Position(loc[0], loc[1]))[0]
    else:
        pointedEntity = None
        # TODO: manage if mouse pointed to the ui

def _drawEntityPointer():
    if pointedEntity == None:
        return
    else:
        pass # TODO: draw entity pointer with thin rectangles


# TODO: this close call includes: socket kill call, kafka end of service call
def _closeApplication():
    global isRunning
    isRunning = False
    pygame.font.quit()
    pygame.quit()
    exit()
