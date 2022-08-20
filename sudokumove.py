from turtle import pos
from sudokutile import Sudokutile

class SudokuMove:
    def __init__(self, tile: Sudokutile, value: int):
        self.tile = tile
        self.value = value
#
    
    def __repr__(self):
        return f"{self.tile.col+1}/{self.tile.row+1}={self.value}"
        

class SudokuMoveBranch(SudokuMove):
    def __init__(self, tile:Sudokutile, value:int, possibleMoves):
        """possibleMoves: list of (tile,value) pairs"""
        super().__init__(tile,value)
        self.possibleMoves=possibleMoves
    
    def removePossibleMove(self,tile,value):
        if (tile,value) in self.possibleMoves:
            self.possibleMoves.remove((tile,value))
    
    def __repr__(self):
        text=SudokuMove.__repr__(self) + "\n ("
        text=text+" ".join(map(lambda x: f"{x[0].col+1}/{x[0].row+1}={x[1]}", self.possibleMoves))+")"
        return text

if __name__=="__main__":
    t1=Sudokutile(0,0)
    t2=Sudokutile(1,0)
    t3=Sudokutile(2,0)
    m1=SudokuMove(t1,3,None)
    m2=SudokuMove(t2,4,m1)
    m3=SudokuMoveBranch(t3,5,m2,[(t3,2),(t3,4)])

    for m in m1,m2,m3:
        print(m)