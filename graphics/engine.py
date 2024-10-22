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
entityControls: list[tuple[pygame.Rect, Callable]] = []


def start(socket_app: Callable):
    global gameMap
    global uiFont

    display = _initObjects(socket_app)

    while True:
        event = pygame.event.wait()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT_CLICK:
                _processClick(*pygame.mouse.get_pos())
        elif event.type == Taxi.MoveEvent:
            gameMap.relocateEntity(event.taxi, event.oldPos)
        elif event.type == pygame.VIDEORESIZE:
            gameMap.resizeDisplay()
            uiFont = pygame.font.Font(pygame.font.get_default_font(), size=int(gameMap.pxboxWidth * 0.6))
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            _closeApplication()

        gameMap.display.fill("black")
        gameMap.render()
        _drawui(display)
        _drawEntityPointer(display)
        _drawEntityInfo(display)
        pygame.display.flip()


def start_passive(socket_app: Callable, e: Entity):
    global gameMap
    global uiFont
    global pointedEntity

    display = _initObjects(socket_app)
    pointedentity = e

    while True:
        event = pygame.event.wait()

        if event.type == Taxi.MoveEvent:
            gameMap.relocateEntity(event.taxi, event.oldPos)
        elif event.type == pygame.VIDEORESIZE:
            gameMap.resizeDisplay()
            uiFont = pygame.font.Font(pygame.font.get_default_font(), size=int(gameMap.pxboxWidth * 0.6))
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            _closeApplication()

        gameMap.display.fill("black")
        gameMap.render()
        _drawui(display)
        _drawEntityPointer(display)
        _drawEntityInfo(display)
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


def _initObjects(socket_app: Callable) -> pygame.Surface:
    global gameMap
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
    return display


def _processClick(x, y):
    global pointedEntity
    global entityControls
    BUTTON = 0; FUNC = 1
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
        for control in entityControls:
            if control[BUTTON].collidePoint(x, y):
                control[FUNC]() # Do something with pointedEntity
                return
        pointedEntity = None


def _drawEntityPointer(display: pygame.Surface):
    global pointedEntity
    if pointedEntity is None or pointedEntity.pos is None:
        return
    lightBlue = (0, 188, 227)
    _drawPointer(display, *gameMap.pxgetPos(*pointedEntity.pos.toTuple()), lightBlue)


def _drawPointer(display: pygame.Surface, px_x: int | float, px_y: int | float, color):
    cursorOffset = gameMap.pxboxWidth * 0.2
    px_x -= cursorOffset
    px_y -= cursorOffset
    pxLength = gameMap.pxboxWidth * 0.5
    pxWidth = gameMap.pxboxWidth * 0.15

    pygame.draw.rect(display, color, pygame.Rect(px_x, px_y, pxWidth, pxLength))
    pygame.draw.rect(display, color, pygame.Rect(px_x, px_y, pxLength, pxWidth))

    cursorOffset *= 2.1
    pygame.draw.rect(display, color, pygame.Rect(
        px_x, px_y + gameMap.pxboxWidth + cursorOffset - pxLength, pxWidth, pxLength))
    pygame.draw.rect(display, color, pygame.Rect(
        px_x, px_y + gameMap.pxboxWidth + cursorOffset - pxWidth, pxLength, pxWidth))

    pygame.draw.rect(display, color, pygame.Rect(
        px_x + gameMap.pxboxWidth + cursorOffset - pxLength, px_y, pxLength, pxWidth))
    pygame.draw.rect(display, color, pygame.Rect(
        px_x + gameMap.pxboxWidth + cursorOffset - pxWidth, px_y, pxWidth, pxLength))

    pygame.draw.rect(display, color, pygame.Rect(
        px_x + gameMap.pxboxWidth + cursorOffset - pxWidth, px_y + gameMap.pxboxWidth + cursorOffset - pxLength, pxWidth, pxLength))
    pygame.draw.rect(display, color, pygame.Rect(
        px_x + gameMap.pxboxWidth + cursorOffset - pxLength, px_y + gameMap.pxboxWidth + cursorOffset - pxWidth, pxLength, pxWidth))


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
                curLogHead += " central"
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
    global entityControls
    global gameMap
    global uiFont
    if pointedEntity is None: return

    px_x = ((display.get_width() / 3) * 2) + (display.get_width() * 0.04)
    px_y = (display.get_height() / 2) - (gameMap.pxboxWidth * ((len(pointedEntity.__dict__) // 2) +2))
    widgetWidth = (display.get_width() / 3) - (display.get_width() * 0.08)
    widgetHeight = gameMap.pxboxWidth * (len(pointedEntity.__dict__) +4)
    borderRadius = display.get_height() * 0.03

    pygame.draw.rect(display, "white", pygame.Rect(px_x, px_y, widgetWidth, widgetHeight), width=2, border_radius=int(borderRadius))
    obj_properties = [
        type(pointedEntity).__name__, 
        "Id: " + (str(pointedEntity.id) if type(pointedEntity) == Taxi else chr(pointedEntity.id)),
        "Current state: " + ["STANDBY", "WAITING", "BUSY", "INCONVENIENCE"][pointedEntity.logType], 
        "Position: " + (str(pointedEntity.pos.toTuple()) if pointedEntity.pos is not None else "not located"),
        "Destination: " + (str(pointedEntity.dst.toTuple()) if pointedEntity.dst is not None else "none")
    ]

    #TODO: dinamically add properties

    aux_x = px_x + (widgetWidth * 0.06)
    _renderTxtBox(display, px_x, px_y, widgetWidth, gameMap.pxboxWidth, (1, type(pointedEntity).__name__, "white"), visibleBox = False)

    aux_y = px_y
    for p in obj_properties:
       aux_y += gameMap.pxboxWidth
       display.blit(uiFont.render(p, True, "white"), (aux_x, aux_y))

    #TODO: Finish to draw buttons and add functions (could be lambdas


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
        if visibleBox:
            pygame.draw.line(display, "white", (vertBarX, px_y), (vertBarX, px_y + height))
        charSize = uiFont.size(txt)
        xoffset = vertBarX - charSize[0] - inboxOriginX
        display.blit(uiFont.render(txt, True, color), (vertBarX - charSize[0] - (xoffset / 2), px_y + height - charSize[1] - ((height - charSize[1]) / 2)))

        inboxOriginX = vertBarX


def _closeApplication():
    global isRunning
    isRunning = False
    pygame.font.quit()
    pygame.quit()
    exit()
