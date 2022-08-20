from multiprocessing.util import is_abstract_socket_namespace
from turtle import back
import pygame
import argparse
from globals import GLOBALS as G
from sudokutile import Sudokutile
from random import choice,randrange
from sudokumove import *


def draw_sudoku():
    """Draw complete Sudoko field."""
    for t in G.sudoku:
        t.draw(G.screen)
    for i in range(1,3):
        pygame.draw.line(G.screen, (0,0,0), (i*3*G.tile_w, 0), (i*3*G.tile_w,G.scr_h),3)
        pygame.draw.line(G.screen, (0,0,0), (0, i*3*G.tile_w), (G.scr_h, i*3*G.tile_w),3)
    pygame.display.flip()

def is_stuck():
    """Test for stuck, returns True if at least one field has no numbers left to fit."""
    for x in G.sudoku:
        if x.get_entropy()==0 and x.is_resolved()==False:
            return True
    return False

def is_solved():
    """Test for complete, returns True if all fields are resolved."""
    for x in G.sudoku:
        if not x.is_resolved(): 
            return False
    return True

def recalculate_constraints():
    """Remove all constraints from all fields and re-calculate all constraints on non-resolved fields.
    Set constraints to emtpy set on resolved fields."""
    for t in G.sudoku:
        t.constraints={1,2,3,4,5,6,7,8,9}
    for t in G.sudoku:
        if t.is_resolved():
           constrain_others(t)
           t.constraints=set() 

def constrain_others(tile):
    """constrain all fields in the same group, row and col of a given tile based on its value."""
    if tile.is_resolved==False: return
    val = tile.value
    # constrain row, col and group
    for t in [x for x in G.sudoku if x!=tile if x.row == tile.row or x.col==tile.col or x.group==tile.group]:
        t.constrain(val)

def backtrack():
    """Undo all unambiguos moves until a branchpoint in the move tree is found.
    returns list of possible moves.
    """
    branch_found=False
    while not branch_found:
        m = G.movetrace.pop()
        branch_found = m.__class__ is SudokuMoveBranch
        # undo move
        m.tile.value=None
    if branch_found:
        recalculate_constraints()
        return m.possibleMoves
    raise RuntimeError("Backtrack tracked beyond the start of the solution trace! Unsolvable?!")

def make_move(tile,value):
    """Makes a single move (tile, value)."""
    tile.resolve(value)
    constrain_others(tile)

def make_single_move(tile,value):
    """Makes a single non-ambiguous move (tile, value) and records it to the move trace."""
    make_move(tile,value)
    G.movetrace.append(SudokuMove(tile,value))

def make_random_move(possible_moves):
    """Picks a random move out of a list of possible moves and records a branch point to the move trace.
    If number of possible moves is 1, records a normal non-ambiguous move to the trace.
    """
    if len(possible_moves)==1:
        t,v = possible_moves[0]
        G.movetrace.append(SudokuMove(t,v))
    else:
        t,v=choice(possible_moves)
        possible_moves.remove((t,v))
        G.movetrace.append(SudokuMoveBranch(t,v,possible_moves))
    make_move(t,v)


def make_iteration():
    """execute a single solver iteration."""
    # Cases:
    #  1. soduku is solved --> do nothing and return
    #  2. Stuck state --> backtrack till last branchpoint, pick new move from branchpoint's list of possibilities
    #  3. not stuck, and smallest entropy == 1 (i.e. unambiguous moves) --> 
    #     resolve *one* unambiguous moves and trace it! (do not resolve all together!!! will cause inconsistencies!)
    #  4. not stuck and smallest entropy is >1 (branch point) --> collect all possible moves, select one (remove it from list)
    #     and resolve chosen tile. trace Branchpoint 
    
    # case 1
    if is_solved(): 
        return
    # case 2
    if is_stuck():
        # if possible moves in a given branch point is 0 (i.e. no further possible moves)
        # then this branch is exhausted. Need to backtrack one level further
        # until possible moves are found
        # if we step beyond the beginning (i.e. the first move has exhausted all possibilities)
        # then this sudoku is unsolvable. Will raise a runtime exception
        #print_move_trace()
        n_moves = 0
        while n_moves == 0:
            possible_moves=backtrack()
            n_moves=len(possible_moves)
        make_random_move(possible_moves)
        return
    # cases 3 and 4, collect possible moves
    unresolved = [x for x in G.sudoku if not x.is_resolved()]
    min_entropy = min(map(lambda x:x.get_entropy(),unresolved))
    candidates = [x for x in G.sudoku if x.get_entropy() == min_entropy]
    possible_moves = [(t,v) for t in candidates for v in t.constraints]
    # case 3
    if min_entropy==1:
        t,v=choice(possible_moves)
        make_single_move(t,v)
        return
    # case 4
    if min_entropy >1:
        make_random_move(possible_moves)
        return
    # THIS SHOULD NEVER HAPPEN:
    raise RuntimeError(f"Unrecognized Case in make_iteration() encountered!\nmin_entropy = {min_entropy}")

def setcaption(paused):
    if paused:
        pygame.display.set_caption(f"Sudoku solver (paused - press space to continue, r to restart)")
    else:
        pygame.display.set_caption(f"Sudoku solver (press space to pause)")

def print_move_trace():
    print("Trace of past move branches:")
    for m in G.movetrace:
        if m.__class__ is SudokuMoveBranch:
            #print (" + ",end="") 
            print(m)           

def get_trace_depth():
    branches=[x for x in G.movetrace if x.__class__ is SudokuMoveBranch]
    moves = [len(x.possibleMoves) for x in branches]
    return len(branches),sum(moves)

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
                    if paused:
                        initialize_sudoku()
                        paused=False
                        setcaption(paused)
                elif ev.key == pygame.K_t:
                    print_move_trace()
        if not paused:
            make_iteration()
            b,m=get_trace_depth()
            pygame.display.set_caption(f"Sudoku solver - trace depth = {b} moves left = {m}")
            draw_sudoku()
            if is_solved():
                paused=True


def initialize_sudoku():
    G.sudoku = [Sudokutile(r,c) for r in range(9) for c in range(9)]
    G.movetrace = []
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