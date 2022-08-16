import pygame
import argparse
from globals import GLOBALS as G
from sudokutile import Sudokutile
from random import choice,randrange

G.sudoku = []

def is_stuck():
    for x in G.sudoku:
        if x.get_entropy()==0 and x.is_resolved()==False:
            return True
    return False

def constrain_others(tile):
    if tile.is_resolved==False: return
    val = tile.value
    # constrain row
    for t in [x for x in G.sudoku if x!=tile if x.row == tile.row ]:
        t.constrain(val)
    # constrain col
    for t in [x for x in G.sudoku if x!=tile if x.col == tile.col ]:
        t.constrain(val)
    # constrain grp
    for t in [x for x in G.sudoku if x!=tile if x.group == tile.group ]:
        t.constrain(val)

def is_solved():
    for x in G.sudoku:
        if not x.is_resolved(): 
            return False
    return True
    
def make_iteration():
    unresolved = [x for x in G.sudoku if not x.is_resolved()]
    if is_solved(): return
    min_entropy = min(unresolved, key=lambda x:x.get_entropy()).get_entropy()
    candidates = [x for x in G.sudoku if x.get_entropy() == min_entropy]
    tile_to_change = choice(candidates)
    value = choice(list(tile_to_change.constraints))
    tile_to_change.resolve(value)
    constrain_others(tile_to_change)    

def draw_sudoku():
    for t in G.sudoku:
        t.draw(G.screen)
    for i in range(1,4):
        pygame.draw.line(G.screen, (0,0,0), (i*3*G.tile_w, 0), (i*3*G.tile_w,G.scr_h),3)
        pygame.draw.line(G.screen, (0,0,0), (0, i*3*G.tile_w), (G.scr_h, i*3*G.tile_w),3)
    pygame.display.flip()

def setcaption(paused):
    if paused:
        pygame.display.set_caption(f"Sudoku solver (paused - press space to continue)")
    else:
        pygame.display.set_caption(f"Sudoku solver (press space to pause)")


def mainloop():
    running=True
    paused=True
    setcaption(paused)
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running=False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running=False
                elif ev.key == pygame.K_SPACE:
                    paused = not paused
                    setcaption(paused)
                elif ev.key == pygame.K_r:
                    if is_solved():
                        initialize_sudoku()
                        paused=False
                        setcaption(paused)
        if not paused:
            if is_stuck():
                initialize_sudoku()
            if not is_solved():
                make_iteration()
            else:  
                pause=True
                pygame.display.set_caption("Sudou solver - solved (press R to restart)")
            draw_sudoku()


def initialize_sudoku():
    G.sudoku = [Sudokutile(r,c) for r in range(9) for c in range(9)]
    if G.preset:
        for t in G.sudoku:
            p = G.preset[t.row][t.col]
            if p in "123456789":
                t.resolve(int(p))
                constrain_others(t)
    draw_sudoku()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sudoku",required=False,help="sudoku preset file. Should contain 9 lines with 9 characters each.\n1-9 will be put into sudoku grid, any other char will be left empty.")
    args=parser.parse_args()
    G.preset=[]
    if args.sudoku:
        print(f"Loading sudoku {args.sudoku}")
        with open(args.sudoku,"r") as f:
            for l in f: G.preset.append(l) 
    pygame.init()
    G.screen = pygame.display.set_mode((G.scr_w,G.scr_h))
    print(f"tilesize : {G.tile_w}")
    initialize_sudoku()
    mainloop()



if __name__=="__main__": main()