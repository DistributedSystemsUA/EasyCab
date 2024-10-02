from __future__ import annotations # For not unfinished declarations
from enum import Enum
from dataclasses import dataclass
from typing import ClassVar
import pygame

M_X = 0
M_Y = 1

class Move(Enum) :
    UP = (0, -1)
    UP_RIGHT = (1, -1)
    RIGHT = (1, 0)
    DOWN_RIGHT = (1, 1)
    DOWN = (0, 1)
    DOWN_LEFT = (-1, 1)
    LEFT = (0, -1)
    UP_LEFT = (-1, -1)

@dataclass
class Position :
    x: int = 0
    y: int = 0

    def moveTo(self, dst: Position):
        direction = (0,0)
        if dst.x > self.x :
            direction[M_X] = 1
        elif dst.x < self.x :
            direction[M_X] = -1

        if dst.y > self.y :
            direction[M_Y] = 1
        elif dst.y < self.y :
            direction[M_Y] = -1
        
        self.x = direction[M_X]
        self.y = direction[M_Y]

    def pivot(self, p: Position, direction: Move):
        self.x = p.x + direction.value[M_X]
        self.y = p.y + direction.value[M_Y]

    def __hash__(self):
        return hash((self.x, self.y))


class LogType(Enum):
    STANDBY = 0
    WAITING = 1,
    BUSY = 2,
    INCONVENIENCE = 3


@dataclass
class Entity :
    id: int = 0
    logType: int = 0
    pos: Position = None
    dst: Position = None


@dataclass(init = False)
class Taxi(Entity) :
    NextTaxiId: ClassVar[int] = 1
    OrphanTaxis: ClassVar[list[int]] = []

    currentClient: Client = None

    def __init__(self, origin: Position, dst: Position = 0):
        if not Taxi.OrphanTaxis :
            self.id = Taxi.NextClientId
            Taxi.NextClientId += 1
        else :
            self.id = Taxi.OrphanTaxis.pop(0)

        self.logType = LogType.STANDBY.value
        self.pos = origin
        self.dst = dst


    def __del__(self):
        Taxi.OrphanTaxis.append(self.id)


    def move(self):
        if dst is None: return

        self.pos.moveTo(self.dst)
        if self.pos == self.dst :
            if self.currentClient is not None:
                if self.logType == LogType.BUSY.value :
                    self.finishService()
                else : # WAITING so start service
                    self.logType = LogType.BUSY.value
                    self.currentClient.logType = Logtype.BUSY.value
                    self.dst = self.currentClient.dst
            else :
                self.dst = None
                self.logType = LogType.STANDBY.value


    def aquireClient(self, c: Client):
        if c is None or self.currentClient is not None :
            print(f'ERROR: the taxi {self.id} can\'t aquire a new client because is carrying {self.currentClient}')
            return

        c.currentTaxi = self
        c.logType = LogType.WAITING.value
        self.currentClient = c
        self.logType = LogType.WAITING.value
        self.dst = c.pos


    def finishService(self, newDst: Position = None):
        if self.currentClient is None :
            print(f'ERROR: the taxi {self.id} is not being used, can\'t finish service')
            return

        self.currentClient.pos = self.pos
        self.currentClient.dst = None
        self.currentClient.logType = LogType.STANDBY.value if self.pos == self.dst else LogType.INCONVENIENCE.value
        self.currentClient.currentTaxi = None
        self.currentClient = None
        if newDst is not None :
            self.dst = newDst # logType keeps busy
        else :
            self.logType = LogType.STANDBY.value



@dataclass(init = False)
class Client(Entity) :
    NextClientId: ClassVar[int] = ord('a')
    NextDestinationId: ClassVar[int] = ord('A')
    OrphanClients: ClassVar[list[int]] = []
    OrphanDestinations: ClassVar[list[int]] = []

    dstId: int = 0

    def __init__(self, origin: Position, destination: Position):
        if not Client.OrphanClients :
            self.id = Client.NextClientId
            Client.NextClientId += 1
        else :
            self.id = Client.OrphanClients.pop(0)

        if not Client.OrphanDestinations :
            self.dstId = Client.NextDestinationId
            Client.NextDestinationId += 1
        else :
            self.dstId = Client.OrphanDestinations.pop(0)

        self.logType = LogType.WAITING.value
        self.pos = origin


    def __del__(self):
        Client.OrphanClients.append(self.id)


class Map :
    def __init__(self, surface: pygame.Surface, width: int = 20, height: int = 20, *entities: Entity):
        self.surface = surface
        if(width < 2 or height < 2):
            raise ValueError('Values of the map are too small. Minimums are: width = 2, height = 2')
        self.width = width
        self.height = height

        self.entities = {}
        self.positionedEntities = {}
        self.addEntities(entities)
        self.surface = surface


    def isInside(self, p: Position):
        return p.x >= 0 and p.x < self.width and p.y >= 0 and p.y <= self.height


    def addEntities(self, *entities: Entity):
        if entities is None : return

        for e in entities :
            if self.isInside(e.pos) :
                self.entities[e.id] = e
                self.positionedEntities[e.pos] = e
            else :
                print(f'The entity {e} is not inside the map')


    def getEntity(self, eId: int) -> Entity:
        if eId in self.entities :
            return self.entities[eId]
        else :
            return None


    def locateEntity(self, p: Position):
        if p in self.positionedEntities:
            return self.positionedEntities[p]
        else :
            return None

    def removeEntity(*entities: Entity):
        for e in entities:
            del self.entities[e.id]
            del self.positionedEntities[e.pid]


    def render(self):
        # Need to set the self.pxUpperCorner = Position
        return 0 # TODO: render full map on the surface


    # Updates (moves) one position one step or finishes a Service (if done)
    def update(self, p: Position):
        return 0 # TODO: rewrite any change in positions (see the most elegant way to connect services with map updates)
