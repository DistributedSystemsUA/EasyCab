import engine
import time

from entities import *


def main():
    engine.gameMap.addEntities(*engine.randEntities(15))
    l = [e for _, e in engine.gameMap.entities.items()]
    while engine.isRunning:
        for e in l:
            if isinstance(e, Taxi):
                e.move()
        time.sleep(1)
        pass

if __name__ == "__main__" :
    engine.start(main)

