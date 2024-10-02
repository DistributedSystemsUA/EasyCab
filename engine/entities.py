from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar
from position import *


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
            self.id = Taxi.NextTaxiId
            Taxi.NextTaxiId += 1
        else :
            self.id = Taxi.OrphanTaxis.pop(0)

        self.logType = LogType.STANDBY.value
        self.pos = origin
        self.dst = dst


    def __del__(self):
        Taxi.OrphanTaxis.append(self.id)


    def move(self):
        if dst is None: return

        unrenderP = Position(self.pos.x, self.pos.y)
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
        self.OrphanClients.append(self.id)
        self.OrphanDestinations.append(self.dstId)

