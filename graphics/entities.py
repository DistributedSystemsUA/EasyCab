from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, NamedTuple
from position import *
import pygame
import threading


class LogType(Enum):
    STANDBY = 0
    WAITING = 1
    BUSY = 2
    INCONVENIENCE = 3


class Location(NamedTuple):
    ID: int
    pos: Position


@dataclass
class Entity :
    id: int = 0
    logType: int = 0
    pos: Position = None
    dst: Position = None


@dataclass(init = False)
class Taxi(Entity):
    MoveEvent: ClassVar[int] = pygame.event.custom_type()
    UnlocateClient: ClassVar[int] = pygame.event.custom_type()
    LocateClient: ClassVar[int] = pygame.event.custom_type()
    JustRender: ClassVar[int] = pygame.event.custom_type()

    currentClient: Client = None
    lock = threading.Lock()

    def __init__(self, own_id: int, origin: Position, dst: Position = None):
        self.id = own_id
        self.logType = LogType.STANDBY.value
        self.pos = origin
        self.dst = dst


    def __eq__(self, other):
        return isinstance(other, Taxi) and self.id == other.id and self.pos == other.pos and self.logType == other.logType and self.dst == other.dst


    def move(self):
        if self.dst is None: return
        if self.logType == LogType.INCONVENIENCE.value:
            self.logType = LogType.BUSY.value

        self.lock.acquire()
        oldPosition = self.pos # old pos immutable = mem security
        self.pos = self.pos.getPivotTo(self.dst)
        self.lock.release()

        if self.pos == self.dst :
            if self.currentClient is not None:
                if self.logType == LogType.BUSY.value :
                    self.finishService()
                else :
                    self.startService()
            else :
                self.dst = None
                self.logType = LogType.STANDBY.value
        pygame.event.post(pygame.event.Event(Taxi.MoveEvent, {"taxi" : self, "oldPos" : oldPosition}))


    def stop(self):
        self.lock.acquire()
        self.logType = LogType.INCONVENIENCE.value
        pygame.event.post(pygame.event.Event(Taxi.JustRender))
        self.lock.release()


    def assignClient(self, c: Client) -> bool:
        if c is None or c.dst is None or self.currentClient is not None:
            return False

        self.lock.acquire()
        self.currentClient = c
        self.logType = LogType.WAITING.value
        self.dst = c.pos
        c.currentTaxi = self
        c.logType = LogType.WAITING.value
        self.lock.release()
        
        return True


    def isBusy(self) -> bool:
        return self.dst is not None


    #############################
    #     Internal functions    #
    #############################


    def startService(self):
        self.lock.acquire()
        self.logType = LogType.BUSY.value
        self.currentClient.logType = LogType.BUSY.value
        self.dst = self.currentClient.dst
        self.lock.release()
        pygame.event.post(pygame.event.Event(Taxi.UnlocateClient, {"client" : self.currentClient}))


    def finishService(self, newDst: Position = None):
        if newDst is not None:
            serviceDst = Position(*self.dst.toTuple())
            self.dst = newDst
            self.logType = LogType.WAITING.value
        else:
            self.logType = LogType.STANDBY.value

        if self.currentClient is not None:
            self.lock.acquire()
            if self.currentClient.logType == LogType.BUSY.value:
                self.currentClient.pos = Position(*self.pos.toTuple())

                if serviceDst == self.pos:
                    self.currentClient.dst = None #Destination reached if taxi has arrived
                    self.currentClient.logType = LogType.STANDBY.value
                else:
                    self.currentClient.logType = LogType.WAITING.value

            self.currentClient.currentTaxi = None
            self.lock.release()

            pygame.event.post(pygame.event.Event(Taxi.LocateClient, {"client" : self.currentClient}))

            self.lock.acquire()
            self.currentClient = None
            self.lock.release()


@dataclass(init = False)
class Client(Entity) :
    NextClientId: ClassVar[int] = ord('a')
    OrphanClients: ClassVar[list[int]] = []

    dstId: int = 0

    def __init__(self, origin: Position, destination: Position = None):
        if not Client.OrphanClients :
            self.id = Client.NextClientId
            Client.NextClientId += 1
        else :
            self.id = Client.OrphanClients.pop(0)

        self.logType = LogType.STANDBY.value
        self.pos = origin
        self.currentTaxi = None
        self.dst = destination

    def __del__(self):
        Client.OrphanClients.append(self.id)


    def setDstLocation(loc: Location):
        self.dst = Position(*loc.pos.toTuple()) # TODO: make the location system null
        self.dstId = loc.ID


    def hasTaxi(self) -> bool:
        return self.currentTaxi is not None

