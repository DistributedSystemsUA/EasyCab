from entities import *
import math
import pygame


class GameMap :
    def __init__(self, display: pygame.Surface, width: int = 20, *entities: Entity):
        self.display = display
        if(width < 2):
            raise ValueError('ERROR: cannot instantiate Map. The side length must be 2 at minimum')
        self.width = width

        self.entities = {}
        self.locatedEntities = {}
        self.locations = {}
        self.addEntities(*entities)
        self.display = display
        self.resizeDisplay()


    def resizeDisplay(self):
        self.pxWidth = (self.display.get_width() / 3) * 1
        self.pxboxWidth = self.pxWidth / (self.width +1) # +1 for position marker boxes

        self.pxLoc= Position(
            (self.display.get_width() / 3) + 10, 
            (self.display.get_height() / 2) - (self.pxWidth / 2))

        self.font = pygame.font.Font(pygame.font.get_default_font(), size=int(self.pxboxWidth * 0.6))


    def isInside(self, p: Position):
        return p.x >= 1 and p.x <= self.width and p.y >= 1 and p.y <= self.width


    # Will return None if the pixel position is not inside
    def getBoxLoc(self, px_x, px_y) -> (int, int):
        if px_x < self.pxLoc.x + self.pxboxWidth or px_x > self.pxLoc.x + self.pxWidth \
                or px_y < self.pxLoc.y + self.pxboxWidth or px_y > self.pxLoc.y + self.pxWidth:
            return None

        return (math.floor((px_x - self.pxLoc.x) / self.pxboxWidth), math.floor((px_y - self.pxLoc.y) / self.pxboxWidth))


    def addEntities(self, *entities: Entity):
        if entities is None : return

        for e in entities :
            if self.isInside(e.pos) :
                if self.entities.get(e.id) is not None:
                    raise ValueError(f'Identification collision, duplicated id: {str(e)}')
                self.entities[e.id] = e
                if self.locatedEntities.get(e.pos) is None:
                    self.locatedEntities[e.pos] = [e]
                else:
                    self.locatedEntities[e.pos].append(e)
            else :
                print(f'The entity {e} is not inside the map')


    def addLocations(self, *locations: Location):
        for l in locations:
            if self.isInside(l.pos):
                self.locations[l.ID] = l


    def relocateEntity(self, e: Entity, oldPos: Position = None) -> bool:
        if not self.isInside(e.pos):
            return False

        if self.locatedEntities.get(e.pos) is None:
            self.locatedEntities[e.pos] = [e]
        else:
            self.locatedEntities[e.pos].append(e)

        if oldPos is not None and (e_list := self.locatedEntities.get(oldPos)) is not None and e in e_list:
            del e_list[e_list.index(e)]
        return True


    def unlocateEntity(self, e: Entity) -> bool:
        if e.pos is None or self.locatedEntities.get(e.pos) is None or e not in self.locatedEntities.get(e.pos):
            return False
        e_list = self.locatedEntities[e.pos]
        del e_list[e_list.index(e)]
        e.pos = None
        return True


    def locateEntities(self, p: Position) -> list[Entity]:
        if self.locatedEntities.get(p) is None:
            return None
        return self.locatedEntities.get(p)


    def removeEntity(*entities: Entity):
        for e in entities:
            del self.entities[e.id]
            positionedEntities = self.locatedEntities[e.pos]
            del positionedEntities[positionedEntities.index(e)]


    def render(self):
        for i in range(1, self.width +1):
            # Horizontal lines and coordinates
            self.renderInboxText(f'{i}', self.pxgetPos(i, 0))
            pygame.draw.line(self.display, "white", self.pxgetPos(0, i), self.pxgetPos(self.width + 1, i))

            # Vertical lines and coordinates
            self.renderInboxText(f'{i}', self.pxgetPos(0, i))
            pygame.draw.line(self.display, "white", self.pxgetPos(i, 0), self.pxgetPos(i, self.width + 1))

        # Last lines to complete map
        pygame.draw.line(self.display, "white", self.pxgetPos(0, self.width + 1), self.pxgetPos(self.width + 1, self.width + 1))
        pygame.draw.line(self.display, "white", self.pxgetPos(self.width + 1, 0), self.pxgetPos(self.width + 1, self.width + 1))
        
        renderPriorities = []
        for _, e in self.entities.items():
            if isinstance(e, Taxi):
                renderPriorities.append(e)
                continue
            self.renderEntity(e)

        for l in self.locations.values():
            self.renderLocation(l)

        for e in renderPriorities:
            self.renderEntity(e)


    def renderEntity(self, e: Entity):
        if e.pos is None:
            return

        entityColor = "yellow" # Client color by default
        entityTxt = f'{e.id}'
        if isinstance(e, Taxi):
            entityColor = ["red", "green", "green", "red"][e.logType]
            if e.logType == LogType.INCONVENIENCE.value: entityTxt += "!"

            if e.currentClient is not None and e.currentClient.logType == LogType.BUSY.value:
                entityTxt += f'{chr(e.currentClient.id)}'
        else:
            entityTxt = f'{chr(e.id)}'

        self.renderInboxText(entityTxt, self.pxgetPos(*e.pos.toTuple()), "black", entityColor)


    def renderLocation(l: int | Location):
        if isinstance(l, int):
            l = self.locations[l.ID]
        self.renderInboxText(f'{chr(l.ID)}', self.pxgetPos(*e.currentClient.dst.toTuple()), "black", "blue")


    def pxgetPos(self, x: int | float, y: int | float) -> tuple:
        return (self.pxLoc.x + (self.pxboxWidth * x), self.pxLoc.y + (self.pxboxWidth * y))


    def renderInboxText(self, txt: str, pxPos: tuple[int | float, int | float], color = None, backgroundColor = None):
        if color is None:
            color = "white"
        
        charSize = self.font.size(txt)
        xoffset = (self.pxboxWidth - charSize[0]) / 2
        yoffset = (self.pxboxWidth - charSize[1]) / 2

        if backgroundColor is not None: # The render is a block
            blockOffset = 0.03
            pxPos = (pxPos[0] + (self.pxboxWidth * blockOffset), pxPos[1] + (self.pxboxWidth * blockOffset))
            txtToRender = pygame.Surface((self.pxboxWidth, self.pxboxWidth))
            txtToRender.fill(backgroundColor)
            txtToRender.blit(self.font.render(txt, True, color), (xoffset, yoffset))
            self.display.blit(txtToRender, pxPos)
        else:
            txtToRender = self.font.render(txt, True, color)
            self.display.blit(txtToRender, (pxPos[0] + xoffset, pxPos[1] + yoffset))

