import pygame
import threading
from random import randint
from typing import Callable

from entities import *
from game_map import *


LEFT_CLICK = 1
RIGHT_CLICK = 3

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
            gameMap.relocateEntity(event.taxi, event.oldPos)
        elif event.type == pygame.VIDEORESIZE:
            gameMap.resizeDisplay()
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            _closeApplication()

        gameMap.display.fill("black")
        gameMap.render()
        _drawEntityPointer(display)
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
    if loc is not None and (l := gameMap.locateEntities(Position(loc[0], loc[1]))) is not None and l:
        pointedEntity = l[0]
        if not isinstance(pointedEntity, Taxi):
            for i in range(1,len(l)):
                if isinstance(l[i], Taxi):
                    pointedEntity = l[i]
                    break
    else:
        pointedEntity = None
        # TODO: manage if mouse pointed to the ui (at right, where the buttons will be)


def _drawEntityPointer(display: pygame.Surface):
    if pointedEntity is not None:
        pxbaseLoc = gameMap.pxgetPos(*pointedEntity.pos.toTuple())
        cursorOffset = gameMap.pxboxWidth * 0.1
        pxbaseLoc[0] -= cursorOffset
        pxbaseLoc[1] -= cursorOffset
        pxLength = gameMap.pxboxWidth * 0.3
        pxWidth = gameMap.pxboxWidth * 0.03
        lightBlue = (255, 200, 200)

        pygame.draw.rect(display, lightBlue, pygame.Rect(pxbaseLoc, (pxLength, pxWidth)))
        pygame.draw.rect(display, lightBlue, pygame.Rect(pxbaseLoc, (pxWidth, pxLength)))

        pygame.draw.rect(display, lightBlue, pygame.Rect(
            pxbaseLoc[0], pxbaseLoc[1] + gameMap.pxboxWidth + (2 * cursorOffset) - pxLength, pxWidth, pxLength))
        pygame.draw.rect(display, lightBlue, pygame.Rect(
            pxbaseLoc[0], pxBaseLoc[1] + gameMap.pxboxWidth + (2 * cursorOffset) - pxWidth, pxLength, pxWidth))

        pygame.draw.rect(display, lightBlue, pygame.Rect(
            pxbaseLoc[0] + gameMap.pxBoxWidth + (2 * cursorOffset) - pxLength, pxbaseLoc[1], pxLength, pxWidth))
        pygame.draw.rect(display, lightBlue, pygame.Rect(
            pxbaseLoc[0] + gameMap.pxBoxWidth + (2 * cursorOffset) - pxWidth, pxbaseLoc[1], pxWidth, pxLength))

        pygame.draw.rect(display, lightBlue, pygame.Rect(
            pxbaseLoc[0] + gameMap.pxBoxWidth + (2 * cursorOffset) - pxWidth, pxbaseLoc[1] + gameMap.pxboxWidth + (2 * cursorOffset) - pxLength, pxWidth, pxLength))
        pygame.draw.rect(display, lightBlue, pygame.Rect(
            pxbaseLoc[0] + gameMap.pxboxWidth + (2 * cursorOffset) - pxLength, pxbaseLoc[1] + gameMap.pxboxWidth + (2 * cursorOffset) - pxWidth, pxLength, pxWidth))


# TODO: this close call includes: socket kill call, kafka end of service call
def _closeApplication():
    global isRunning
    isRunning = False
    pygame.font.quit()
    pygame.quit()
    exit()
