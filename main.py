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
    
def make_move(tile:Sudokutile, value):
    """Resolves a single field "tile" to "value"."""
    tile.resolve(value)
    constrain_others(tile)
    print(f"resolved {tile.col+1}/{tile.row+1} to {value}")

def format_tiles(tiles):
    """returns a readable string for a list of tiles."""
    return ", ".join(map(lambda x: f"{x.col+1}/{x.row+1}",tiles))

def make_iteration():
    """Make single solution step."""
    # 1. if solved, do nothing
    if is_solved():
        return
    # 2. if unique spots exist, resolve them
    uniques = [x for x in G.sudoku if len(x.constraints) == 1]
    if len(uniques):
        # Pick any, might as well choose the first in the list, 
        # next iteration will pick up the next
        # it's constraints will have exactly 1 element, so pop() it
        make_move(uniques[0],uniques[0].constraints.pop())
        return
    # 3. so no fully constrained tile was found... be more clever now
    #    Algo:
    #    iterate through all *groups*
    #      find all tiles which are a) not resolved
    #      for all numbers 1...9 
    #        skip if number is alread in that group
    #        find all potential candiates in that group, which have number is their constraints set
    #        if only one element in result set, resolve that tile and return
    for group in range(9):
        group_tiles = [x for x in G.sudoku if x.group == group]
        group_values = [x.value for x in group_tiles]
        unresolved = set([x for x in group_tiles if not x.is_resolved()])
        blocked = set()
        for v in range(1,10):
            if v in group_values: continue
            candidates = {x for x in unresolved if v in x.constraints}
            print(f"for value {v} in group {group} found these candidates: {format_tiles(candidates)}")
            if len(candidates)==1:
                # So for value "v" we have only one candidate left, resolve it it v and return.
                # we have made a move so return to mainloop
                make_move(candidates.pop(),v)
                return
    # Now what?!
    # Pick a random move from the tiles with the lowest entropy?
    min_entropy = min([x.get_entropy() for x in G.sudoku])
    moves = [(t,v) for t in G.sudoku for v in t.constraints]
    t,v = choice(moves)
    # We might get stuck later on... but that's life if the sudoku has no unique solution
    make_move(t,v)
    return
    raise RuntimeError("make_iteration didn't know how to continue")

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
            elif  is_solved():
                pause=True
                pygame.display.set_caption("Sudou solver - solved (press R to restart)")
            else:  
                make_iteration()
            draw_sudoku()
            #paused=True


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