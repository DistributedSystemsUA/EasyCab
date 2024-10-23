import path_load
import engine
from entities import Taxi
from position import Position

def main():
    t = Taxi(Position(9,3))
    t.dst = Position(1,2)

    engine.gameMap.addEntities(t)
    t.move()

if __name__=="__main__":
    engine.start(main)
