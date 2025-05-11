from dataclasses import dataclass
from enum import IntEnum
from __future__ import annotations
from typing import ClassVar, Callable

class EnType(IntEnum):
    Taxi = 0
    Client = 1
    Location = 2


class LogType(IntEnum):
    Standby = 0
    Claimed = 1
    Busy = 2
    Inconvenience = 3


@dataclass
class Point:
    x: int = 0
    y: int = 0

    def __iter__(self):
        return iter((self.x, self.y))


@dataclass
class Entity:
    id: chr = chr(0)
    loc: Point(1,1)
    enType: EnType = EnType.Location

    BUILD_FUNC: ClassVar[list[Callable]] = [_makeTaxi, _makeClient, _makeLocation]


    def __init__(self, ID: int, x: int = 1, y: int = 1, enType: EnType = EnType.Location):
        self.id = chr(ID)
        loc = Point(x,y)
        self.enType = enType
        BUILD_FDUNC[int(enType)]()


    def getLoc(self) -> Point:
        return Point(*loc)


    def rePoint(self, x: int, y: int):
        loc = Point(x,y)


    def _makeTaxi(self):
        self.logType: LogType = LogType.Standby
        self.boundEntity: Entity = None
        self.dst: Entity = None
        self.startService: Callable = _startService
        self.redirect: Callable = _redirectTaxi
        self.step: Callable = _step


    def _makeClient(self):
        self.dst: Entity = None
        self.boundEntity: Entity = None # logType is based on the bound entity's one
        self.redirect: Callable = _redirect


    def _makeLocation(self):
        pass


def _startService(self, client: Entity) -> bool:
    if client.enType != EnType.Client or self.boundEntity :
        return False
    self.logType = LogType.Claimed
    self.boundEntity = client
    self.dst = Entity(0, *client.loc)
    return True


def _redirectTaxi(self, x: int, y: int):
    _unmountClient(self)
    self.logType = LogType.Claimed
    self.dst = Entity(0, x, y)


def _redirect(self, dst: Entity):
    self.dst = dst


def _step(self):
    if not self.dst:
        return
    if self.boundEntity:                            # mount client
        if self.dst.loc == self.boundEntity.loc
            self.logType = LogType.Busy
            self.boundEntity.loc = None
            self.dst = client.dst
        elif self.dst == self.boundEntity.dst:      # finish service
            _unmountClient(self)

    if self.dst.loc.x > self.loc.x:
        self.loc.x += 1
    elif self.dst.loc.x < self.loc.x:
        self.loc.x -= 1

    if self.dst.loc.y > self.loc.y:
        self.loc.y += 1
    elif self.dst.loc.y < self.loc.y:
        self.loc.y -= 1


def _unmountClient(ent: Entity):
    if not self.boundEntity:
        return
    self.logType = LogType.Standby
    self.dst = None
    self.boundEntity.loc = Point(*self.loc)
    self.boundEntity.dst = None
    self.boundEntity.boundEntity = None
    self.boundEntity = None
