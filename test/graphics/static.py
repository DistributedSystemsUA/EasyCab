from path_load import *

import engine
from entities import *
import time


def main():
    l = engine.randEntities(15)
    engine.gameMap.addEntities(*l)

    while engine.isRunning:
        time.sleep(1)


if __name__=="__main__":
    engine.start(main)
