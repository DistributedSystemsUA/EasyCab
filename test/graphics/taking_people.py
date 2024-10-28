import path_load
import engine
<<<<<<< HEAD
from entities imoprt *

# TODO: add render event to aquireClient
def main():
    entities = randEntities(15)
    gameMap.addEntities(*entities)

    taxis = []; clients = []
    for e in entities:
        if isinstance(t, Taxi):
=======
from entities import *
import time

# TODO: add render event to aquireClient
def main():
    entities = engine.randEntities(20)
    engine.gameMap.addEntities(*entities)

    taxis = []; clients = []
    for e in entities:
        if isinstance(e, Taxi):
>>>>>>> juanma
            taxis.append(e)
        else:
            clients.append(e)

    while engine.isRunning:
        for t in taxis:
<<<<<<< HEAD
            # TODO: make infrastructure for taxis to aquire the clients
            pass
=======
            if not t.isBusy():
                for c in clients:
                    if not c.hasTaxi() and c.dst is not None:
                        t.assignClient(c)
                        break
            t.move()
        time.sleep(1)
>>>>>>> juanma


if __name__=="__main__":
    engine.start(main)
