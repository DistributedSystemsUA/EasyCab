from __future__ import annotations # For not unfinished declarations
from enum import Enum
from dataclasses import dataclass
from typing import ClassVar

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

    def toTuple(self):
        return (self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))
