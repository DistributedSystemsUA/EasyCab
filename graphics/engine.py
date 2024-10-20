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

    gameMap.render()
    _uidraw(display)
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
        _uidraw(display)
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
    global pointedEntity
    loc = gameMap.getBoxLoc(x, y)
    if loc is not None and (l := gameMap.locateEntities(Position(loc[0], loc[1]))) is not None and l:
        isTaxi = False
        for e in l:
            if isinstance(e, Taxi):
                pointedEntity = e
                isTaxi = True
                break

        if not isTaxi:
            pointedEntity = l[0]
    else:
        pointedEntity = None
        # TODO: manage if mouse pointed to the ui (at right, where the buttons will be)


def _drawEntityPointer(display: pygame.Surface):
    if pointedEntity is None:
        return

    pxbaseLoc = gameMap.pxgetPos(*pointedEntity.pos.toTuple())
    pxbaseLoc = [pxbaseLoc[0], pxbaseLoc[1]] # To support item assignment
    cursorOffset = gameMap.pxboxWidth * 0.2
    pxbaseLoc[0] -= cursorOffset
    pxbaseLoc[1] -= cursorOffset
    pxLength = gameMap.pxboxWidth * 0.5
    pxWidth = gameMap.pxboxWidth * 0.15
    lightBlue = (0, 188, 227)

    pygame.draw.rect(display, lightBlue, pygame.Rect(pxbaseLoc, (pxLength, pxWidth)))
    pygame.draw.rect(display, lightBlue, pygame.Rect(pxbaseLoc, (pxWidth, pxLength)))

    cursorOffset *= 2.1
    pygame.draw.rect(display, lightBlue, pygame.Rect(
        pxbaseLoc[0], pxbaseLoc[1] + gameMap.pxboxWidth + cursorOffset - pxLength, pxWidth, pxLength))
    pygame.draw.rect(display, lightBlue, pygame.Rect(
        pxbaseLoc[0], pxbaseLoc[1] + gameMap.pxboxWidth + cursorOffset - pxWidth, pxLength, pxWidth))

    pygame.draw.rect(display, lightBlue, pygame.Rect(
        pxbaseLoc[0] + gameMap.pxboxWidth + cursorOffset - pxLength, pxbaseLoc[1], pxLength, pxWidth))
    pygame.draw.rect(display, lightBlue, pygame.Rect(
        pxbaseLoc[0] + gameMap.pxboxWidth + cursorOffset - pxWidth, pxbaseLoc[1], pxWidth, pxLength))

    pygame.draw.rect(display, lightBlue, pygame.Rect(
        pxbaseLoc[0] + gameMap.pxboxWidth + cursorOffset - pxWidth, pxbaseLoc[1] + gameMap.pxboxWidth + cursorOffset - pxLength, pxWidth, pxLength))
    pygame.draw.rect(display, lightBlue, pygame.Rect(
        pxbaseLoc[0] + gameMap.pxboxWidth + cursorOffset - pxLength, pxbaseLoc[1] + gameMap.pxboxWidth + cursorOffset - pxWidth, pxLength, pxWidth))


def _uidraw(display: pygame.Surface):
    global gameMap
    global pointedEntity

    # TODO: left -> map info, right -> pointedEntity info and buttons
    # TODO: left -> map info, right -> pointedEntity info and buttons
    pxuiLoc = (display.get_width() * 0.05, display.get_height() * 0.1)
    pxuiWidth = gameMap.pxLoc.x - pxuiLoc[0] - (display.get_width() * 0.05)

    # TODO: make text box ui


# IMPORTANT: the first tuple argument is the portion of the space taken, must be a float between 0 and 1
def _renderTxtBox(display: pygame.Surface, px_x, px_y, width, height, *txtPartitions: tuple[float, str, tuple[int, int, int] | str]):
    if not txtPartitions:
        return
    pygame.draw.line(display, "white", (px_x, px_y), (px_x + width, px_y))
    pygame.draw.line(display, "white", (px_x, px_y), (px_x, px_y + height))
    pygame.draw.line(display, "white", (px_x + width, px_y), (px_x + width, px_y + height))
    pygame.draw.line(display, "white", (px_x, px_y + height), (px_x + width, px_y + height))
    for portion, txt, color in txtPartitions:
        pass
        #TODO: if portion does not match with 0 to 1 float model, take the rest of the space and break


# TODO: this close call includes: socket kill call, kafka end of service call
def _closeApplication():
    global isRunning
    isRunning = False
    pygame.font.quit()
    pygame.quit()
    exit()
