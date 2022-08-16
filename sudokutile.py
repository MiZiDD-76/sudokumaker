from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
import pygame
from globals import GLOBALS as G

pygame.font.init()
class Sudokutile:
    smallfont = pygame.font.SysFont("",int(G.tile_w/3))
    bigfont = pygame.font.SysFont("",G.tile_w)
    def __init__(self, row, col):
        self.row=row
        self.col=col
        self.group=int(col/3)+int(row/3)*3
        self.constraints = {1,2,3,4,5,6,7,8,9}
        self.text_pitch = G.tile_w/3
        self.value = None

    # def __getattribute__(self, __name: str):
    #     if __name == "entropy":
    #         return len(self.constraints)
    #     elif __name in self.__dict__.keys:
    #         return self.__dict__[__name]
    #     else:
    #         raise NameError(__name)

    def constrain(self,value_to_remove):
        if value_to_remove in self.constraints:
            self.constraints.remove(value_to_remove)

    def resolve(self,value):
        self.value=value
        self.constraints=set()

    def is_resolved(self):
        return self.value != None

    def get_entropy(self):
        return len(self.constraints)

    def __str__(self):
        return f"Sudokutile at Row {self.row} / Col {self.col} in Group {self.group}: entropy {self.get_entropy()}"

    def draw(self, surface:pygame.surface.Surface):
        r = pygame.Rect(self.col*G.tile_w, self.row*G.tile_w ,G.tile_w-1 ,G.tile_w-1)
        if self.is_resolved(): 
            color = (200,200,200)
        elif self.get_entropy()==1:
            color = (255,255,0)
        else:
            color = pygame.Color(255,0,0).lerp(pygame.Color(0,255,0),self.get_entropy()/9)
        surface.fill(color,r)
        if self.is_resolved():
            text=Sudokutile.bigfont.render(str(self.value),True,(0,0,0))
            surface.blit(
                text,
                (r.centerx-text.get_width()/2, r.centery-text.get_height()/2)
            )
        else:
            for y in range(3):
                for x in range(3):
                    n = x + y*3 + 1
                    if n in self.constraints:
                        pass
                        surface.blit(
                            Sudokutile.smallfont.render(str(n),False,(0,0,0)),
                            (r.left + x*self.text_pitch + 4, r.top + y*self.text_pitch + 4)        
                        )
