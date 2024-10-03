from entities import *
import pygame


class GameMap :
    def __init__(self, display: pygame.Surface, width: int = 20, *entities: Entity):
        self.display = display
        if(width < 2):
            raise ValueError('ERROR: cannot instantiate Map. The side length must be 2 at minimum')
        self.width = width

        self.entities = {}
        self.locatedEntities = {}
        self.addEntities(*entities)
        self.display = display
        self.resizeDisplay()
        self.font = pygame.font.Font(pygame.font.get_default_font(), size=int(self.pxboxWidth * 0.7))


    def resizeDisplay(self):
        self.pxLoc= Position(
            (self.display.get_width() / 3) + 10, 
            (self.display.get_width() / 3) * 0.25)
        self.pxWidth = (self.display.get_width() / 3) * 1
        self.pxboxWidth = self.pxWidth / self.width


    def isInside(self, p: Position):
        return p.x >= 1 and p.x < self.width and p.y >= 1 and p.y <= self.width


    # Will return None if the pixel position inside is not inside
    def getBoxLocation(px_x, px_y) -> (int | float, int | float):
        if px_x < self.pxLoc.x + self.pxboxWidth or px_x > self.pxLoc.x + self.pxWidth \
                or px_y < self.pxLoc.y + self.pxboxWidth or px_y > self.pxLoc.y + self.pxWidth:
            return None

        # TODO: finish function, return pxLocation


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
        return self.locatedEntities.get(p)


    def removeEntity(*entities: Entity):
        for e in entities:
            del self.entities[e.id]
            del self.locatedEntities[e.pos]


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

        for _, e in entities:
            entityColor = "yellow" # Client color by default
            entityTxt = f'{e.id}'
            if isinstance(e, Taxi):
                entityColor = ["red", "green", "green", "red"][e.logType.value]
                entityTxt += f'{e.currentClient.id}' if e.currentClient is not None else ''
            elif e.dst is not None:
                self.renderInboxText(f'{e.dstId}', e.dst.toTuple(), "black", entityColor) # Render client's destination

            self.renderInboxText(entityTxt, e.pos.toTuple(), "black", entityColor)


    def pxgetPos(self, x: int | float, y: int | float) -> tuple:
        return (self.pxLoc.x + (self.pxboxWidth * x), self.pxLoc.y + (self.pxboxWidth * y))


    def renderInboxText(self, txt: str, pxPos: tuple[int | float, int | float], color = None, backgroundColor = None):
        if color is None:
            color = "white"
        
        charSize = self.font.size(txt)
        xoffset = (self.pxboxWidth - charSize[0]) / 2
        yoffset = (self.pxboxWidth - charSize[1]) / 2

        if backgroundColor is not None:
            txtToRender = pygame.Surface((self.pxBoxWidth, self.pxBoxWidth))
            txtToRender.fill(backgroundColor)
            txtToRender.blit(self.font.render(txt, True, color), (xoffset, yoffset))
            self.display.blit(self.font.render(txt, True, color), pxPos)
        else:
            txtToRender = self.font.render(txt, True, color)
            self.display.blit(txtToRender, (pxPos[0] + xoffset, pxPos[1] + yoffset))

