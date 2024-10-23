from __future__ import annotations # For not finished define declarations
from enum import Enum

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


class Position :
    def __init__(self, x: int, y: int) :
        self.x = x
        self.y = y

    def move(self, direction: Move) :
        self.x = direction.value[M_X]
        self.y = direction.value[M_Y]

    def pivot(self, p: Position, direction: Move)
        self.x = p.x + direction.value[M_X]
        self.y = p.y + direction.value[M_Y]


class Service :
    NextTaxiId = 1
    NextClientId = ord('a')
    NextDestinationId = ord('A')

    OrphanTaxis = []
    OrphanClients = []
    OrphanDestinations = []

    # Class contains: taxi, taxiLog, client, clientLog, destination, destinationPos
    def __init__(self, genTaxi: bool, genClient: bool, dst: Position = None):
        if genTaxi :
            if Service.OrphanTaxis :
                self.taxi = Service.OrphanTaxis.pop(0)
            else :
                self.taxi = Service.NextTaxiId
                Service.NextTaxiId += 1
        else :
            self.taxi = 0
        self.taxiLog = 0 # Log zero always means nothing to do or waiting for an event

        if genClient :
            if Service.OrphanClients :
                self.client = Service.OrphanClients.pop(0)
            else :
                self.client = Service.NextClientId
                Service.NextClientId += 1
        else :
            self.client = 0
        self.clientLog = 0

        if dst is not None :
            if Service.OrphanDestinations :
                self.destination = Service.OrphanDestinations.pop(0)
            else :
                self.destination = Service.NextDestinationId
                Service.NextDestinationId += 1
        else :
            self.destination = 0
        self.destinationPos = dst


    # Overwrites the current service values with the other one's that are created and available
    # If any identificator is overwritten, is left as orphan and auto managed
    # Empty values of the other do not overwrite self values
    def mergeWith(self, other: Service):
        if other.taxi > 0 :
            if self.taxi > 0 :
                Service.OrphanTaxis.append(self.taxi)
            self.taxi = other.taxi

        if other.client > 0 :
            if self.client > 0 :
                Service.OrphanClients.append(self.client)
            self.client = other.client

        self.destination = other.destination

        
class Map :
    def __init__(self, width: int = 20, height: int = 20, *startServices: (Position, Service))
        if(width < 1 or height < 0)
            raise ValueError('A map creation has received a negative number')
        self.width = width
        self.height = height
        self.data = []
        for _ in range(width * height):
            self.data = None
        for p, srv in startServices:
            self.setService(p, srv)

    def isInside(self, p: Position)
        return p.x >= 0 and p.x < self.width and p.y >= 0 and p.y <= self.height


    def getService(self, p: Position) -> Service:
        return self.data[p.x + (p.x * self.height)] if self.isInside(p) else None


    def setService(self, p: Position, srv: Service):
        if not self.isInside(p):
            raise ValueError(f'The position {p} is not inside the map. Failed to set taxi service')
        self.data[p.x + (p.x * self.height)] = srv

    def render(self, surface: pygame.Surface, px_width: int = 0, px_height: int = 0):
        return 0 # TODO: render full map on the screen

    def update(self, surface: pygame.Surface):
        return 0 # TODO: rewrite any change in positions (see the most elegant way to connect services with map updates)
