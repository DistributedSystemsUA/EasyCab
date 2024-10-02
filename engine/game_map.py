from entities import *
import pygame


class GameMap :
    def __init__(self, display: pygame.Surface, mapWidth: int = 20, *entities: Entity):
        self.display = display
        if(mapWidth < 2):
            raise ValueError('ERROR: cannot instantiate Map. The side length must be 2 at minimum')
        self.mapWidth = mapWidth

        self.entities = {}
        self.locatedEntities = {}
        self.addEntities(entities)
        self.display = display

        self.pxLoc= Position(
            (display.get_width() // 3) + 10, 
            (display.get_width() // 3) * 2.5)
        self.sidepxLength = int((display.get_width() // 3) * 1.3)
        self.boxpxLength = self.sidepxLength // self.mapWidth
        self.font = pygame.font.Font(pygame.font.get_default_font(), size=boxpxLength)


    def isInside(self, p: Position):
        return p.x >= 0 and p.x < self.width and p.y >= 0 and p.y <= self.height


    def addEntities(self, *entities: Entity):
        if entities is None : return

        for e in entities :
            if self.isInside(e.pos) :
                self.entities[e.id] = e
                if self.locatedEntities.get(e.pos) is None:
                    self.locatedEntities[e.pos] = [e]
                else:
                    self.locatedEntities[e.pos].append(e)
            else :
                print(f'The entity {e} is not inside the map')


    def getEntity(self, eId: int) -> Entity:
        if eId in self.entities :
            return self.entities[eId]
        else :
            return None


    def locateEntities(self, p: Position) -> list[Entity]:
        if self.locatedEntities.get(p) is None:
            return None
        return self.locatedEntities.get


    def removeEntity(*entities: Entity):
        for e in entities:
            del self.entities[e.id]
            del self.locatedEntities[e.pos]


    def render(self):
        for i in range(1, self.mapWidth +1):
            curNumber = self.font.render(f'{i}', True, "white")

            # Horizontal lines and coordinates
            startPos = (self.pxLoc.x, self.pxLoc.y + (self.boxpxLength * i))
            endPos = (self.pxLoc.x + self.sidepxLength, self.pxLoc.y + (self.boxpxLength * i))
            self.display.blit(curNumber, startPos)
            pygame.draw.line(self.display, "white", startPos, endPos)

            # Vertical lines and coordinates
            startPos = (self.pxLoc.x + (self.boxpxLength * i), self.pxLoc.y)
            endPos = (self.pxLoc.x + (self.boxpxLength * i), self.pxLoc.y + self.sidepxLength)
            self.display.blit(curNumber, startPos)
            pygame.draw.line(self.display, "white", startPos, endPos)

        # Last horizontal line
        pygame.draw.line(self.display, "white", (self.pxLoc.x, self.pxLoc.y + (self.boxpxLength * self.mapWidth)))
        
        #TODO: draw placed elements

        self.display.flip() # TODO: probably get out to be able to render ui
