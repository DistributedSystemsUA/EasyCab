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
uiFont: pygame.font.Font = None
entityButtons: list[pygame.Rect] = []


def start(socket_app: Callable):
    global gameMap
    global isRunning
    global pointedEntity
    global uiFont

    pygame.init()
    pygame.font.init()

    display = pygame.display.set_mode((800,600), pygame.RESIZABLE)
    gameMap = GameMap(display, MAP_WIDTH)
    uiFont = pygame.font.Font(pygame.font.get_default_font(), size=int(gameMap.pxboxWidth * 0.6))

    gameMap.render()
    _drawui(display)
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
        _drawui(display)
        _drawEntityPointer(display)
        pygame.display.flip()


def randPos(mapSideLength: int):
    return Position(randint(1, mapSideLength), randint(1, mapSideLength))


def randEntity() -> Entity:
    t = Taxi(randPos(MAP_WIDTH), randPos(MAP_WIDTH)) if randint(0,1) == 0 else Client(randPos(MAP_WIDTH), randPos(MAP_WIDTH))
    t.logType = LogType.WAITING.value
    return t


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


def _drawui(display: pygame.Surface):
    global gameMap
    global pointedEntity

    pxuiLoc = (display.get_width() * 0.02, display.get_height() * 0.1)
    pxuiWidth = gameMap.pxLoc.x - pxuiLoc[0] - (display.get_width() * 0.02)

    _renderTxtBox(display, *pxuiLoc, pxuiWidth, gameMap.pxboxWidth, (1, "*** Easy CAB Release 1 ***", "white"))
    pxuiLeftLoc = [pxuiLoc[0], pxuiLoc[1] + gameMap.pxboxWidth]
    pxuiRightLoc = [pxuiLoc[0] + (pxuiWidth * 0.5), pxuiLoc[1] + (gameMap.pxboxWidth * 2)]
    _renderTxtBox(display, *pxuiLeftLoc, pxuiWidth, gameMap.pxboxWidth, (0.5, "Taxis", "white"), (1, "Clientes", "white"))
    pxuiLeftLoc[1] += gameMap.pxboxWidth

    propertiesBox = ((0.2, "Id.", "white"), (0.5, "Destino", "white"), (1, "Estado", "white"))
    _renderTxtBox(display, *pxuiLeftLoc, pxuiWidth / 2, gameMap.pxboxWidth, *propertiesBox)
    _renderTxtBox(display, *pxuiRightLoc, pxuiWidth / 2, gameMap.pxboxWidth, *propertiesBox)
    pxuiLeftLoc[1] += gameMap.pxboxWidth
    pxuiRightLoc[1] += gameMap.pxboxWidth

    for e in gameMap.entities.values():
        if isinstance(e, Taxi):
            if e.logType == LogType.INCONVENIENCE.value:
                curColor = "red"
                curLogHead = "KO."
            else:
                curColor = "white"
                curLogHead = "OK."

            if e.currentClient != None:
                if e.currentClient.dst == e.dst:
                    curDst = chr(e.currentClient.dstId)
                else:
                    curDst = chr(e.currentClient.id)
                curLogHead += " Servicio " + curDst
            elif e.logType in [LogType.WAITING.value, LogType.BUSY.value]:
                curLogHead += " servir base"
                curDst = f"({e.dst.x},{e.dst.y})"
            else:
                curLogHead += " Parado"
                curDst = "-"

            entityInfo = ((0.2, str(e.id), curColor), (0.5, curDst, curColor), (1, curLogHead, curColor))
            _renderTxtBox(display, *pxuiLeftLoc, pxuiWidth / 2, gameMap.pxboxWidth, *entityInfo)
            pxuiLeftLoc[1] += gameMap.pxboxWidth
        else:
            curLogHead = "OK."
            if e.currentTaxi is not None:
                curLogHead += " Taxi " + str(e.currentTaxi.id)
            entityInfo = ((0.2, chr(e.id), "white"), (0.5, chr(e.dstId if e.dst is not None else "-"), "white"), (1, curLogHead, "white"))
            _renderTxtBox(display, *pxuiRightLoc, pxuiWidth / 2, gameMap.pxboxWidth, *entityInfo)
            pxuiRightLoc[1] += gameMap.pxboxWidth


def _drawEntityInfo(display: pygame.Surface):
    global entityButtons
    global uiFont
    if pointedEntity is None: return

    #TODO: finish and plan entity buttons


# IMPORTANT: the first tuple argument is the portion of the space taken, must be a float between 0 and 1
def _renderTxtBox(display: pygame.Surface, px_x, px_y, width, height, *txtPartitions: tuple[float, str, tuple[int, int, int] | str], visibleBox: bool = True):
    global uiFont

    if visibleBox:
        pygame.draw.line(display, "white", (px_x, px_y), (px_x + width, px_y))
        pygame.draw.line(display, "white", (px_x, px_y), (px_x, px_y + height))
        pygame.draw.line(display, "white", (px_x + width, px_y), (px_x + width, px_y + height))
        pygame.draw.line(display, "white", (px_x, px_y + height), (px_x + width, px_y + height))

    inboxOriginX = px_x
    for portion, txt, color in txtPartitions:
        vertBarX = px_x + (width * portion)
        pygame.draw.line(display, "white", (vertBarX, px_y), (vertBarX, px_y + height))
        charSize = uiFont.size(txt)
        xoffset = vertBarX - charSize[0] - inboxOriginX
        display.blit(uiFont.render(txt, True, color), (vertBarX - charSize[0] - (xoffset / 2), px_y + height - charSize[1] - ((height - charSize[1]) / 2)))

        inboxOriginX = vertBarX


# TODO: this close call includes: socket kill call, kafka end of service call
def _closeApplication():
    global isRunning
    isRunning = False
    pygame.font.quit()
    pygame.quit()
    exit()
