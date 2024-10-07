import pygame
from map import *
from random import randint

LEFT_CLICK = 1
RIGHT_CLIC = 3


def randPos() -> Position:
    return Position(randint(0,19), randint(0,19))

def randEntity() -> Entity:
    return [Taxi(randPos()), Client(randPos())][randint(0,1)]

def randEntityList(n: int) -> list[Entity]:
    l = []
    for _ in range(n):
        l.append(randEntity())

    return l


if __name__=="__main__":
    pygame.init()
    surface = pygame.display.set_mode((800,600), pygame.RESIZABLE)

    m = Map(surface)
    m.addEntities(*randEntityList(20))
        

    while True:
        for event in pygame.event.get():
            if event.type == pygaem.KEYDOWN:
                k = event.type.key

                if k in [pygame.K_BACKSPACE, pygame.K_ESCAPE]:
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == LEFT_CLICK: # Pointing to taxi or client
