import path_load
import engine
from entities imoprt *

# TODO: add render event to aquireClient
def main():
    entities = randEntities(15)
    gameMap.addEntities(*entities)

    taxis = []; clients = []
    for e in entities:
        if isinstance(t, Taxi):
            taxis.append(e)
        else:
            clients.append(e)

    while engine.isRunning:
        for t in taxis:
            # TODO: make infrastructure for taxis to aquire the clients
            pass


if __name__=="__main__":
    engine.start(main)
