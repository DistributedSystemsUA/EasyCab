from __future__ import annotations # For not unfinished declarations
from enum import Enum
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


class Position :
    def __init__(self, x: int, y: int) :
        self.x = x
        self.y = y

    def __eq__(self, p: Position):
        return self.x == p.x and self.y == p.y

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


    # Merges a service with one another (substitute all values at least they are empty)
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
        self.destinationPos = other.destinationPos


class Map :
    def __init__(self, surface: pygame.Surface, width: int = 20, height: int = 20, *startServices: (Position, Service))
        self.surface = surface
        if(width < 2 or height < 2)
            raise ValueError('Values of the map are too small. Minimums are: width = 2, height = 2')
        self.width = width
        self.height = height

        self.data = []
        for _ in width * height :
            self.data.append(None)
        for pos, srv in startServices :
            self.setService(pos, srv)

        self.surface = surface

    def _idx(self, p) -> int:
        return p.x + (p.y * self.width)
        

    def isInside(self, p: Position)
        return p.x >= 0 and p.x < self.width and p.y >= 0 and p.y <= self.height


    def getService(self, p: Position) -> Service | list:
        return self.data[self._idx(p)] if self.isInside(p) else None


    def setService(self, p: Position, srv: Service):
        if not self.isInside(p):
            raise ValueError(f'The position {p} is not inside the map. Failed to set taxi service')

        if self.data[self._idx(p)] is None :
            self.data[self._idx(p)] = srv
        elif isinstance(self.data[self._idx(p)], Service):
            self.data[self._idx(p)] = [self.data[self._idx(p)], srv]
        else :
            self.data[self._idx(p)].append(srv)


    def render(self):
        # Need to set the self.pxUpperCorner = Position
        return 0 # TODO: render full map on the surface


    # Updates (moves) one position one step or finishes a Service (if done)
    def updateAt(self, p: Position):
        if(self.isInside(p) and hasattr(self, 'pxUpperCorner') and self.getService(p) is not None \
                and self.getService(p).taxi > 0 self.getService(p).destinationPos is not None
        # Position is inside, service is a taxi with an objective, service is not finished
        # So -> current position re-renders as first list element or empty
        # -> moves position
        # -> renders actual position as occupied (maybe getting a representation
        return 0 # TODO: rewrite any change in positions (see the most elegant way to connect services with map updates)
