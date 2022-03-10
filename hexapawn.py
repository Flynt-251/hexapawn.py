from abc import ABC
from json import dumps, loads
from random import choice, random
from time import ctime, strftime
from time import perf_counter
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import *

# Check to ensure external Libraries are installed.
chartsAvailable = False
try:
    import numpy as np
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    chartsAvailable = False
    print("Libraries numpy and matplotlib could not be found. You won't be able to compare AI or view benchmark progress.")
else: chartsAvailable = True

class Pawn(ABC):
    """
    Base Class for all pawns in the game.

    `posX, posY` - Defines position of the pawn on a theoretical board.

    `label` - Creates a custom label for the pawn that can be up to 3 characters long.

    `moveCheck` - Defines whether to check spaces above (-1) or below (1) itself on a board.

    `isPlayer` - Defines if the piece is used by the player or CPU.
    """
    def __init__(self, posX: int, posY: int, label: str = "nil", moveCheck: int = 0, isPlayer: bool = False) -> None:
        self.posX = posX
        self.posY = posY
        if len(label) == 1: self.label = ' '+label+' '
        elif len(label) == 2:  self.label = label+' '
        elif len(label) == 3: self.label = label
        else: self.label = "nil"
        self._moveCheck = moveCheck
        self.isPlayer = isPlayer
    
    def checkMoves(self, board) -> list:
        """
        Verifies where the pawn can/can't move.

        Requires the current board as an argument

        Returns list of 3 boolean values:
        Index 0: Can this piece move left? (Must have an enemy piece)
        Index 1: Can this piece move forward? (Must be vacant)
        Index 2: Can this piece move right? (Must have an enemy piece)
        """
        moves = [False, False, False]

        try: forward = board.board[self.posX+self._moveCheck][self.posY]
        except IndexError: moves[1] = False # "Out of Index"
        else:
            if forward == '   ': moves[1] = True
            else: moves[1] = False # "Occupied"

        try: diagonalLeft = board.board[self.posX+self._moveCheck][self.posY-1]
        except IndexError: moves[0] = False # "Out of Index"
        else:
            if self.posX+self._moveCheck < 0 or self.posY-1 < 0: moves[0] = False # "Not in range"
            elif diagonalLeft == '   ': moves[0] = False # "Unoccupied"
            else:
                if self.isPlayer == (not diagonalLeft.isPlayer):
                    moves[0] = True
                else: moves[0] = False

        try: diagonalRight = board.board[self.posX+self._moveCheck][self.posY+1]
        except IndexError: moves[2] = False # "Out of Index"
        else:
            if self.posX+self._moveCheck < 0 or self.posY+1 > 2: moves[2] = False # "Not in range"
            elif diagonalRight == '   ': moves[2] = False # "Unoccupied"
            else:
                if self.isPlayer == (not diagonalRight.isPlayer):
                    moves[2] = True
                else: moves[2] = False

        return moves

    def getMoves(self, board) -> list:
        """Performs `checkMoves(board)` and converts boolean list to a list of 2D list indexes."""
        moves = []
        canMove = self.checkMoves(board)
        if canMove[0]: moves.append((self.posX+self._moveCheck, self.posY-1))
        if canMove[1]: moves.append((self.posX+self._moveCheck, self.posY))
        if canMove[2]: moves.append((self.posX+self._moveCheck, self.posY+1))
        return moves

    def changePos(self, x: int, y: int) -> None:
        """Updates Pawn position in the game."""
        self.posX = x
        self.posY = y

class WhitePawn(Pawn):
    """
    Player Pieces (Player always goes first)
    
    Defaults: `moveCheck = -1, isPlayer = True`
    """
    def __init__(self, posX: int, posY: int, label: str = "WPx") -> None:
        super().__init__(posX, posY, label, moveCheck=-1, isPlayer=True)

class BlackPawn(Pawn):
    """
    AI Pieces (AI always goes second)
    
    Defaults: `moveCheck = 1, isPlayer = False`
    """
    def __init__(self, posX: int, posY: int, label: str = "BPx") -> None:
        super().__init__(posX, posY, label, moveCheck=1, isPlayer=False)

class hexBoard():
    """
    A 3-by-3 board object used to map pawns and play Hexapawn
    """
    def __init__(self) -> None:
        self.board = [
            [BlackPawn(0,0,"BP1"),BlackPawn(0,1,"BP2"),BlackPawn(0,2,"BP3")],
            ["   ","   ","   "],
            [WhitePawn(2,0,"WP1"),WhitePawn(2,1,"WP2"),WhitePawn(2,2,"WP3")]
        ]
    
    def displayBoard(self) -> None:
        """
        Outputs the contents of the board to the terminal window.

        Intended for testing and debugging.
        """
        labels = []
        for row in self.board:
            data = []
            for square in row:
                if type(square) is WhitePawn or type(square) is BlackPawn:
                    data.append(square.label)
                else: data.append("   ")
            labels.append(data)
        print("    A   B   C")
        print("  +---+---+---+")
        print(f"1 |{labels[0][0]}|{labels[0][1]}|{labels[0][2]}|")
        print("  +---+---+---+")
        print(f"2 |{labels[1][0]}|{labels[1][1]}|{labels[1][2]}|")
        print("  +---+---+---+")
        print(f"3 |{labels[2][0]}|{labels[2][1]}|{labels[2][2]}|")
        print("  +---+---+---+")
    
    def __configPiece(self, x, y) -> None:
        """Sets the position of a pawn, if there is one there."""
        if self.board[x][y] != "   ":
            self.board[x][y].changePos(x,y)
    
    def swap(self, originX: int, originY: int, newLocationX: int, newLocationY: int) -> None:
        """Swaps the contents of two squares."""
        temp = self.board[newLocationX][newLocationY]
        self.board[newLocationX][newLocationY] = self.board[originX][originY]
        self.board[originX][originY] = temp

    def overwriteAndMove(self, sourceX: int, sourceY: int, targetX: int, targetY: int) -> None:
        """
        Moves the contents of the source coordinates to the target coordinates, emptying the old square.

        This method is primarily used for gameplay.
        """
        self.board[targetX][targetY] = self.board[sourceX][sourceY]
        self.board[sourceX][sourceY] = "   "
        self.__configPiece(targetX,targetY)
    
    def returnCaptureString(self) -> str:
        """
        Returns a string version of the board contents, which is used by AI subroutines.

        w - White Pawn
        b - Black Pawn
        o - Empty Space
        """
        output = ""
        for row in self.board:
            for space in row:
                if type(space) is WhitePawn: output += "w"
                elif type(space) is BlackPawn: output += "b"
                else: output += "o"
        return output
    
    def reset(self) -> None:
        """Reset the board to its default layout."""
        self.board = [
            [BlackPawn(0,0,"BP1"),BlackPawn(0,1,"BP2"),BlackPawn(0,2,"BP3")],
            ["   ","   ","   "],
            [WhitePawn(2,0,"WP1"),WhitePawn(2,1,"WP2"),WhitePawn(2,2,"WP3")]
        ]

class ComputerPlayer():
    """
    An AI object to play Hexapawn

    `learnFactor` - The rate at which the AI will learn. The higher, the faster.

    `fileSource` - When passed as a string, will overwrite the AI using a ".hexai" file source.
    """
    def __init__(self, learnFactor: float = 0.01, fileSource: str = None) -> None:
        self.learnFactor = learnFactor
        self.moveArchive = []
        self.layoutLookup = {
            # Turn 2 Layouts
            "bbbowowow": [["A1>A2",1/2,-1], ["A1>B2",1/2,1]], # Image: 2
            "bbbwoooww": [["B1>A2",1/3,1], ["B1>B2",1/3,1], ["C1>C2",1/3,-1]], # Image: 1
            "bbboowwwo": [["A1>A2",1/3,-1], ["B1>B2",1/3,1], ["B1>C2",1/3,1]], # Image: 3
            # Turn 4 Layouts
            "bobwoooow": [["C1>C2",1.0,0]], # Image: 1,6
            "boboowwoo": [["A1>A2",1.0,0]], # Image: 3,6
            "bobbowowo": [["A2>A3",1/2,0],["A2>B3",1/2,0]], # Image: 1,1
            "bbowwboow": [["A1>B2",1/2,0],["B1>A2",1/2,0]], # Image: 1,5
            "obbbwwwoo": [["B1>C2",1/2,0],["C1>B2",1/2,0]], # Image: 2,1
            "bobwobowo": [["C2>B3",1/2,0],["C2>C3",1/2,0]], # Image: 3,1
            "obbowooow": [["C1>B2",1/2,-1],["C1>C2",1/2,1]], # Image: 2,2
            "obbowowoo": [["C1>B2",1/2,-1],["C1>C2",1/2,1]], # Image: 2,3
            "obbobwwoo": [["B1>C2",1/3,-1],["B2>A3",1/3,1],["B2>B3",1/3,1]], # Image: 2,5
            "bobwwoowo": [["A1>B2",1/3,-1],["C1>B2",1/3,1],["C1>C2",1/3,-1]], # Image: 1,3
            "bbowowoow": [["B1>A2",1/3,-1],["B1>B2",1/3,-1],["B1>C2",1/3,1]], # Image: 1,4
            "bobowwowo": [["A1>A2",1/3,-1],["A1>B2",1/3,1],["C1>B2",1/3,-1]], # Image: 3,3
            "obbwowwoo": [["B1>A2",1/3,1],["B1>B2",1/3,-1],["B1>C2",1/3,-1]], # Image: 3,4
            "bobbwooow": [["A1>B2",1/4,0],["C1>B2",1/4,0],["C1>C2",1/4,-1],["A2>A3",1/4,1]], # Image: 1,2
            "bobowbwoo": [["A1>A2",1/4,-1],["A1>B2",1/4,0],["C1>B2",1/4,0],["C2>C3",1/4,1]], # Image: 3,2
            "obbwbooow": [["B1>A2",1/4,-1],["C1>C2",1/4,-1],["B2>B3",1/4,1],["B2>C3",1/4,1]], # Image: 2,4
            # Turn 6 Layouts
            "boowwwooo": [["A1>B2",1.0,0]], # Image: 1,4,1
            "oobwwwooo": [["C1>B2",1.0,0]], # Image: 3,4,1
            "oobbbwooo": [["A2>A3",1/2,0],["B2>B3",1/2,0]], # Image: 1,2,1
            "boobbwooo": [["A2>A3",1/2,0],["B2>B3",1/2,0]], # Image: 1,2,2
            "boobwoooo": [["A1>B2",1/2,0],["A2>A3",1/2,0]], # Image: 1,2,3
            "oboobwooo": [["B1>C2",1/2,0],["B2>B3",1/2,0]], # Image: 2,2,1
            "obowboooo": [["B1>A2",1/2,0],["B2>B3",1/2,0]], # Image: 2,3,1
            "oobwbbooo": [["B2>B3",1/2,0],["C2>C3",1/2,0]], # Image: 2,5,1
            "oobowbooo": [["C1>B2",1/2,0],["C2>C3",1/2,0]], # Image: 2,5,2
            "boowbbooo": [["B2>B3",1/2,0],["C2>C3",1/2,0]], # Image: 3,2,1
            "obowwbooo": [["B1>A2",1/2,-1],["C2>C3",1/2,1]], # Image: 1,5,1
            "obobwwooo": [["B1>C2",1/2,-1],["A2>A3",1/2,1]], # Image: 2,1,1
            "oobbwoooo": [["C1>B2",1/3,1],["C1>C2",1/3,-1],["A2>A3",1/3,1]], # Image: 1,2,4
            "booowbooo": [["A1>A2",1/3,-1],["A1>B2",1/3,1],["C2>C3",1/3,1]], # Image: 3,2,4
        }
        self.gameCount = 0
        self.winCount = 0
        self.benchmarkScore = 0
        self.benchmarkArchive = []
        if fileSource != None:
            with open(fileSource, 'r') as file:
                fileData = loads(file.read())
            self.layoutLookup = fileData["AI_Data"]
            self.gameCount = fileData["games"]
            self.winCount = fileData["wins"]
            self.benchmarkScore = fileData["benchmark"]
            self.benchmarkArchive = fileData["benchmark_history"]

    def archiveMove(self, boardString: str, moveIndex: int) -> None:
        """Add a move and its board layout to the AI's move archive. this is used for learning."""
        self.moveArchive.append((boardString, moveIndex))
    
    def pickMove(self, boardString: str) -> tuple:
        """Select a move given the string layout of the board."""
        moves = self.layoutLookup[boardString]
        if len(moves) == 1: selection = moves[0]
        else:
            selection = random()
            accumulator = 0
            for move in moves:
                accumulator += move[1]
                if accumulator - selection > 0:
                    selection = move
                    break
            if type(selection) is float: raise TypeError(f"AI couldn't pick a move because random value {selection} was not properly allocated a probability. The ComputerPlayer.pickMove() function needs to be modified.")
        output = selection[0].split(">")
        return (output[0], output[1], selection[1], moves.index(selection))
    
    def recordAndPickMove(self, boardString: str) -> tuple:
        """Select a move and automatically add it to the AI move archive."""
        data = self.pickMove(boardString)
        self.archiveMove(boardString, data[3])
        return (data[0],data[1])

    def modifyMoveProbability(self, boardString: str, moveIndex: int, AIWin: bool, overrideFactor: float = None) -> None:
        """Change the chance of a move being picked, depending on whether the AI won."""
        if type(overrideFactor) is float: factor = overrideFactor
        else: factor = self.learnFactor
        if not AIWin: factor -= factor*2
        moves = self.layoutLookup[boardString]
        moveList = moves[moveIndex]
        if len(moves) != 1:
            for move in moves:
                if move is moveList:
                    self.layoutLookup[boardString][self.layoutLookup[boardString].index(move)][1] += factor
                else:
                    self.layoutLookup[boardString][self.layoutLookup[boardString].index(move)][1] -= factor/(len(moves)-1)
                if self.layoutLookup[boardString][self.layoutLookup[boardString].index(move)][1] > 1: self.layoutLookup[boardString][self.layoutLookup[boardString].index(move)][1] = 1
                if self.layoutLookup[boardString][self.layoutLookup[boardString].index(move)][1] < 0: self.layoutLookup[boardString][self.layoutLookup[boardString].index(move)][1] = 0
    
    def learnFromGame(self, AIWin: bool) -> None:
        """Take all moves from the move archive, and apply learning modifications."""
        for move in self.moveArchive:
            self.modifyMoveProbability(move[0], move[1], AIWin)
        self.moveArchive = []
    
    def flushArchive(self) -> None:
        """Empty the move archive"""
        self.moveArchive = []
    
    def exportAI(self, filename: str = 'output.hexai') -> None:
        """Save an AI with a given filename in ".hexai" format by default"""
        output = {
            "games": self.gameCount,
            "wins": self.winCount,
            "benchmark": self.benchmarkScore,
            "benchmark_history": self.benchmarkArchive,
            "AI_Data": self.layoutLookup
        }
        with open(filename,"w") as file:
            finalOutput = dumps(output)
            file.write(finalOutput)
    
    def importAI(self, fileSource: str) -> None:
        """Load an AI from a file source. All data is overwritten."""
        with open(fileSource, 'r') as file:
            fileData = loads(file.read())
        self.layoutLookup = fileData["AI_Data"]
        self.gameCount = fileData["games"]
        self.winCount = fileData["wins"]
        self.benchmarkScore = fileData["benchmark"]
        self.benchmarkArchive = fileData["benchmark_history"]
    
    def benchmark(self) -> int:
        """Produce a score that can be used to compare the skill level of different AIs"""
        score = 0.0
        for moves in self.layoutLookup.values():
            for move in moves:
                score += move[1]*move[2]
        finalScore = int(score*1000)
        if finalScore == 333:
            finalScore = 0
        self.benchmarkScore = finalScore
        self.benchmarkArchive.append(finalScore)
        return finalScore # Max Possible Score is 23,000, Min is -22,000
    
    def perfectAI(self) -> None:
        """Sets Data to produce a "Perfect" AI."""
        for set in self.layoutLookup.items():
            layout, moves = set
            for move in moves:
                if move[2] == 1: self.layoutLookup[layout][moves.index(move)][1] = 1
                if move[2] == 0: self.layoutLookup[layout][moves.index(move)][1] = 0
                if move[2] == -1: self.layoutLookup[layout][moves.index(move)][1] = 0

    def saveGame(self, win: bool) -> None:
        """Save the results of a game and calculate the new Benchmark Score"""
        self.gameCount += 1
        if win: self.winCount += 1
        self.benchmark()
    
    def plotBenchmark(self, display: bool = True, name: str = "AI Record"):
        """
        Use Matplotlib.pyplot and Numpy to display benchmark score.

        `display` - Defines whether `plt.show()` will execute.

        `name` - Set a custom label
        """
        plt.bar([name], self.benchmarkScore, label=name)
        if display: plt.show()
    
    def plotBenchmarkHistory(self, display: bool = True, name: str = "AI Record") -> None:
        """
        Use Matplotlib.pyplot and Numpy to display benchmark score over time.

        `display` - Defines whether `plt.show()` will execute.

        `name` - Set a custom label
        """
        archSize = len(self.benchmarkArchive)
        x = np.linspace(1,archSize,archSize)
        y = np.array(self.benchmarkArchive)
        plt.plot(x,y, label=name)
        print(f"Current Score: {self.benchmarkScore}\nPeak Score: {max(self.benchmarkArchive)}\nAverage Score: {np.average(self.benchmarkArchive)}\nBenchmark calculated {archSize} total times.")
        plt.legend()
        if display: plt.show()
    
    def plotWinsOverGames(self, display: bool = True, name: str = "AI Record") -> None:
        """
        Use Matplotlib.pyplot and Numpy to display wins and losses when testing.

        `display` - Defines whether `plt.show()` will execute.

        `name` - Set a custom label
        """
        x = [name]
        wins = np.array([self.winCount])
        losses = np.array([self.gameCount - self.winCount])
        plt.bar(x, wins, color="b")
        plt.bar(x, losses, bottom=wins, color='r')
        plt.legend(["Wins", "Losses"])
        print(f"Played {self.gameCount} games total, won {self.winCount}. Success rate {round((self.winCount/self.gameCount)*100, 2)} %")
        if display: plt.show()

    def reset(self) -> None:
        """Reset all values to default settings."""
        self.learnFactor = 0.01
        self.moveArchive = []
        self.layoutLookup = {
            # Turn 2 Layouts
            "bbbowowow": [["A1>A2",1/2,-1], ["A1>B2",1/2,1]], # Image: 2
            "bbbwoooww": [["B1>A2",1/3,1], ["B1>B2",1/3,1], ["C1>C2",1/3,-1]], # Image: 1
            "bbboowwwo": [["A1>A2",1/3,-1], ["B1>B2",1/3,1], ["B1>C2",1/3,1]], # Image: 3
            # Turn 4 Layouts
            "bobwoooow": [["C1>C2",1.0,0]], # Image: 1,6
            "boboowwoo": [["A1>A2",1.0,0]], # Image: 3,6
            "bobbowowo": [["A2>A3",1/2,0],["A2>B3",1/2,0]], # Image: 1,1
            "bbowwboow": [["A1>B2",1/2,0],["B1>A2",1/2,0]], # Image: 1,5
            "obbbwwwoo": [["B1>C2",1/2,0],["C1>B2",1/2,0]], # Image: 2,1
            "bobwobowo": [["C2>B3",1/2,0],["C2>C3",1/2,0]], # Image: 3,1
            "obbowooow": [["C1>B2",1/2,-1],["C1>C2",1/2,1]], # Image: 2,2
            "obbowowoo": [["C1>B2",1/2,-1],["C1>C2",1/2,1]], # Image: 2,3
            "obbobwwoo": [["B1>C2",1/3,-1],["B2>A3",1/3,1],["B2>B3",1/3,1]], # Image: 2,5
            "bobwwoowo": [["A1>B2",1/3,-1],["C1>B2",1/3,1],["C1>C2",1/3,-1]], # Image: 1,3
            "bbowowoow": [["B1>A2",1/3,-1],["B1>B2",1/3,-1],["B1>C2",1/3,1]], # Image: 1,4
            "bobowwowo": [["A1>A2",1/3,-1],["A1>B2",1/3,1],["C1>B2",1/3,-1]], # Image: 3,3
            "obbwowwoo": [["B1>A2",1/3,1],["B1>B2",1/3,-1],["B1>C2",1/3,-1]], # Image: 3,4
            "bobbwooow": [["A1>B2",1/4,0],["C1>B2",1/4,0],["C1>C2",1/4,-1],["A2>A3",1/4,1]], # Image: 1,2
            "bobowbwoo": [["A1>A2",1/4,-1],["A1>B2",1/4,0],["C1>B2",1/4,0],["C2>C3",1/4,1]], # Image: 3,2
            "obbwbooow": [["B1>A2",1/4,-1],["C1>C2",1/4,-1],["B2>B3",1/4,1],["B2>C3",1/4,1]], # Image: 2,4
            # Turn 6 Layouts
            "boowwwooo": [["A1>B2",1.0,0]], # Image: 1,4,1
            "oobwwwooo": [["C1>B2",1.0,0]], # Image: 3,4,1
            "oobbbwooo": [["A2>A3",1/2,0],["B2>B3",1/2,0]], # Image: 1,2,1
            "boobbwooo": [["A2>A3",1/2,0],["B2>B3",1/2,0]], # Image: 1,2,2
            "boobwoooo": [["A1>B2",1/2,0],["A2>A3",1/2,0]], # Image: 1,2,3
            "oboobwooo": [["B1>C2",1/2,0],["B2>B3",1/2,0]], # Image: 2,2,1
            "obowboooo": [["B1>A2",1/2,0],["B2>B3",1/2,0]], # Image: 2,3,1
            "oobwbbooo": [["B2>B3",1/2,0],["C2>C3",1/2,0]], # Image: 2,5,1
            "oobowbooo": [["C1>B2",1/2,0],["C2>C3",1/2,0]], # Image: 2,5,2
            "boowbbooo": [["B2>B3",1/2,0],["C2>C3",1/2,0]], # Image: 3,2,1
            "obowwbooo": [["B1>A2",1/2,-1],["C2>C3",1/2,1]], # Image: 1,5,1
            "obobwwooo": [["B1>C2",1/2,-1],["A2>A3",1/2,1]], # Image: 2,1,1
            "oobbwoooo": [["C1>B2",1/3,1],["C1>C2",1/3,-1],["A2>A3",1/3,1]], # Image: 1,2,4
            "booowbooo": [["A1>A2",1/3,-1],["A1>B2",1/3,1],["C2>C3",1/3,1]], # Image: 3,2,4
        }
        self.gameCount = 0
        self.winCount = 0
        self.benchmarkScore = 0
        self.benchmarkArchive = []
    
class MasterPlayer(ComputerPlayer):
    """
    AI Player that acts as a replacement to a Human Player

    Used by training and testing functions to develop AI. Is currently replacable with a Random move function.
    """
    def __init__(self) -> None:
        self.layoutLookup = {
            # Turn 1 Layout (Starting Move)
            "bbbooowww": [["A3>A2",1/3],["B3>B2",1/3],["C3>C2",1/3]],
            # Turn 3 Layouts
            "bobboooww": [["B3>A2",1/3],["B3>B2",1/3],["C3>C2",1/3]],
            "bobwbooww": [["C3>B2",1/2],["C3>C2",1/2]],
            "bbowoboww": [["A2>B1",1/3],["B3>B2",1/3],["B3>C2",1/3]],
            "obbbwowow": [["B2>C1",1/2],["C3>C2",1/2]],
            "obbobowow": [["A3>A2",1/4],["A3>B2",1/4],["C3>B2",1/4],["C3>C2",1/4]],
            "obbbowwwo": [["B3>A2",1/3],["B3>B2",1/3],["C2>B1",1/3]],
            "bobobwwwo": [["A3>A2",1/2],["A3>B2",1/2]],
            "boboobwwo": [["A3>A2",1/3],["B3>B2",1/3],["B3>C2",1/3]],
            # Turn 5 Layouts
            "oobbbooow": [["C3>B2",1/2],["C3>C2",1/2]],
            "boobbooow": [["C3>B2",1/2],["C3>C2",1/2]],
            "boobwboow": [["B2>A1",1/2],["B2>B1",1/2]],
            "oobwboowo": [["A2>A1",1.0]],
            "boowwbowo": [["B2>A1",1/3],["B2>B1",1/3],["B3>C2",1/3]],
            "boobowoow": [["C2>C1",1.0]],
            "boowbwoow": [["C2>C1",1/2],["C3>B2",1/2]],
            "obowbboow": [["A2>A1",1/3],["A2>B1",1/3],["C3>B2",1/3]],
            "obobbwwoo": [["A3>B2",1/3],["C2>B1",1/3],["C2>C1",1/3]],
            "oobbwbwoo": [["B2>B1",1/2],["B2>C1",1/2]],
            "oboobooow": [["C3>B2",1/2],["C3>C2",1/2]],
            "oboobowoo": [["A3>B2",1/2],["A3>A2",1/2]],
            "oobbbooow": [["C3>B2",1/2],["C3>C2",1/2]],
            "obowbboow": [["A2>A1",1/3],["A2>B1",1/3],["C3>B2",1/3]],
            "oobobbwoo": [["A3>A2",1/2],["A3>B2",1/2]],
            "booobbwoo": [["A3>A2",1/2],["A3>B2",1/2]],
            "oobbwwowo": [["B2>B1",1/2],["B3>A2",1/2]],
            "booobwowo": [["C2>C1",1.0]],
            "oobwbwwoo": [["A2>A1",1/2],["A3>B2",1/2]],
            "oobwobwoo": [["A2>A1",1.0]],
            "oboowbwoo": [["A3>A2",1.0]],
            # Turn 7 Layouts
            "ooobwbooo": [["B2>B1",1.0]],
            "ooowbwooo": [["A2>A1",1/2],["C2>C1",1/2]]
        }


def checkEndGame(board: hexBoard) -> bool:
    """Analyses a board and returns whether the board has reached an endgame state."""
    opponentPieces = []
    playerPieces = []
    for space in board.board[0]:
        if type(space) is WhitePawn:
            return True
        if type(space) is BlackPawn:
            opponentPieces.append(space)
    for space in board.board[1]:
        if type(space) is BlackPawn:
            opponentPieces.append(space)
        if type(space) is WhitePawn:
            playerPieces.append(space)
    for space in board.board[2]:
        if type(space) is BlackPawn:
            return True
        if type(space) is WhitePawn:
            playerPieces.append(space)
    if len(opponentPieces) == 0: return True
    if len(playerPieces) == 0 : return True
    else:
        possibleMoves = []
        for piece in opponentPieces:
            possibleMoves.extend(piece.checkMoves(board))
        if True in possibleMoves: return False
        else: return True

def returnCoords(coordString: str) -> tuple:
    """
    Converts Human-Readable Coordinates into 2D list index

    coordString - The user-input string, such as "A3" or "C2". This is not case-sensetive.
    """
    y = coordString[0].lower()
    columnCheck = {"a":0, "b":1, "c":2}
    x = int(coordString[1])-1
    y = columnCheck[y]
    return (x,y)

def inputCoords() -> tuple:
    return returnCoords(input("> "))

def outputCoords(x:int,y:int) -> str:
    """
    Converts 2D list indexes into Human-Readable chess-board coordinates

    x and y correspond to the indexes such that it looks like this: `dataList[x][y]`
    """
    columnCheck = ["A","B","C"]
    column = columnCheck[y]
    row = str(x+1)
    return column+row

def displayPossibleMoves(moves: list) -> dict:
    """Takes a list of moves and outputs them for text-based gameplay"""
    movesOutput = {"CanMove":False, "Moves":[]}
    if len(moves) == 0:
        print("Cannot move this piece!")
        moves.append(False)
        movesOutput["CanMove"] = False
    else:
        movesOutput["CanMove"] = True
        print("Possible moves: ", end='')
        for item in moves:
            movesOutput["Moves"].append((item[0],item[1]))
            print(outputCoords(item[0],item[1]), end='  ')
        print('\n')
    return movesOutput

def moveInput(table: hexBoard) -> bool:
    """Handle user input for a move"""
    moveFinished = False
    try:
        while not moveFinished:
            print("Select Piece:")
            coords = inputCoords()
            piece = table.board[coords[0]][coords[1]]
            if type(piece) is WhitePawn:
                movesList = displayPossibleMoves(piece.getMoves(table))
                if movesList["CanMove"]:
                    print("Move this piece where?")
                    newCoords = inputCoords()
                    if newCoords in movesList["Moves"]:
                        table.overwriteAndMove(coords[0],coords[1],newCoords[0],newCoords[1])
                        moveFinished = True
                    else: print("Not a listed move!")
            elif type(piece) is BlackPawn: print("Not your piece.")
            else: print("No piece there.")
    except KeyboardInterrupt:
        print("Game Stopped.")
        return True
    else: return False

def randomMove(board: hexBoard) -> None:
    """Placeholder Subroutine for AI"""
    pieces = []
    moves = []
    for row in board.board:
        for space in row:
            if type(space) is BlackPawn: pieces.append(space)
    while len(moves) == 0:
        selection = choice(pieces)
        moves = selection.getMoves(board)
    moveChoice = choice(moves)
    board.overwriteAndMove(selection.posX, selection.posY, moveChoice[0], moveChoice[1])

def handleAIMove(move: tuple, board: hexBoard) -> None:
    """Performs move operation after AI has selected a move."""
    sourceSpace = returnCoords(move[0])
    targetSpace = returnCoords(move[1])
    if not(type(board.board[sourceSpace[0]][sourceSpace[1]]) is BlackPawn):
        raise RuntimeError(f"AI has requested move {move} on board layout {board.returnCaptureString()} which cannot occur because the source space does not have a black pawn.")
    if not(targetSpace in board.board[sourceSpace[0]][sourceSpace[1]].getMoves(board)):
        raise RuntimeError(f"AI has requested move {move} on board layout {board.returnCaptureString()}, which is an illegal move.")
    board.overwriteAndMove(sourceSpace[0],sourceSpace[1],targetSpace[0],targetSpace[1])

def handleMasterAIMove(move: tuple, board: hexBoard) -> None:
    """Performs move operation after Master AI has selected a move."""
    sourceSpace = returnCoords(move[0])
    targetSpace = returnCoords(move[1])
    if not(type(board.board[sourceSpace[0]][sourceSpace[1]]) is WhitePawn):
        raise RuntimeError(f"Master AI has requested move {move} on board layout {board.returnCaptureString()} which cannot occur because the source space does not have a white pawn.")
    if not(targetSpace in board.board[sourceSpace[0]][sourceSpace[1]].getMoves(board)):
        raise RuntimeError(f"Master AI has requested move {move} on board layout {board.returnCaptureString()}, which is an illegal move.")
    board.overwriteAndMove(sourceSpace[0],sourceSpace[1],targetSpace[0],targetSpace[1])

def gameCycle(board: hexBoard, ai: ComputerPlayer, learn: bool = False) -> None:
    """Performs one game cycle."""
    humansTurn = True
    interrupt = False
    board.displayBoard()
    while not checkEndGame(board) and not interrupt:
        if humansTurn:
            interrupt = moveInput(board)
        else:
            moveData = ai.recordAndPickMove(board.returnCaptureString())
            handleAIMove(moveData, board)
            print(f"Opponent has moved from {moveData[0]} to {moveData[1]}")
            board.displayBoard()
        humansTurn = not humansTurn
    if not interrupt:
        print("Computer Wins!") if humansTurn else print("Player Wins!")
        if learn: ai.learnFromGame(humansTurn)
    ai.flushArchive()

def autoGame(board: hexBoard, ai: ComputerPlayer, masterAi: MasterPlayer, learn: bool = False, showCommentary: bool = False, returnLogData: bool = False) -> bool:
    """Automates one game of Hexapawn using an AI and master AI object."""
    masterTurn = True
    logData = ""
    #board.displayBoard()
    while not checkEndGame(board):
        if masterTurn:
            moveData = masterAi.pickMove(board.returnCaptureString())
            handleMasterAIMove(moveData, board)
            if showCommentary: print(f"Master Player has moved from {moveData[0]} to {moveData[1]}")
            if returnLogData: logData += f"Master Player has moved from {moveData[0]} to {moveData[1]}\n"
        else:
            moveData = ai.recordAndPickMove(board.returnCaptureString())
            handleAIMove(moveData, board)
            if showCommentary: print(f"Opponent has moved from {moveData[0]} to {moveData[1]}")
            if returnLogData: logData += f"Opponent has moved from {moveData[0]} to {moveData[1]}\n"
            #board.displayBoard()
        masterTurn = not masterTurn
    if masterTurn:
        if showCommentary: print("Computer Wins!")
        if returnLogData: logData += "Computer Won.\n"
        output = True
    else:
        if showCommentary: print("Master Player Wins!")
        if returnLogData: logData += "Master Player Won.\n"
        output = False
    if learn:
        ai.learnFromGame(masterTurn)
        ai.benchmark()
    else: ai.saveGame(masterTurn)
    ai.flushArchive()
    return (output, logData)

def virtualiseGames(ai: ComputerPlayer, gameCount: int = 25, train: bool = False, showCommentary: bool = False, logWithName: str = None) -> tuple:
    """Runs a given quantity of automated games"""
    if gameCount <= 0: raise ValueError("Argument gameCount must be a positive integer above 0.")
    wins = 0
    board = hexBoard()
    masterAI = MasterPlayer()
    if logWithName != None: log = f"Automated Games Log for Hexapawn AI, Started: {ctime()}\n{gameCount} total games, Training: {train}, Commentary: {showCommentary}\n"
    t = perf_counter()

    for i in range(gameCount):
        if logWithName != None: log += f"----- Game {i+1} of {gameCount} -----\n"
        won, gameLog = autoGame(board, ai, masterAI, train, showCommentary, (logWithName != None))
        if won: wins += 1
        if logWithName != None: log += gameLog
        board = hexBoard()

    if logWithName != None:
        with open(logWithName, "a") as file:
            file.write(log)

    time = perf_counter() - t
    return (wins, time)

def initialiseUI():
    """Starts the GUI Application."""
    boardData = hexBoard()
    ai = ComputerPlayer()

    def noCommandYet() -> None:
        print("This button's subroutine has not been implemented yet!")

    def post(string: str = 'Hello World!') -> None:
        textPane.config(state=NORMAL)
        textPane.insert(END, string+'\n')
        textPane.config(state=DISABLED)
    
    def clearTextPane() -> None:
        textPane.config(state=NORMAL)
        textPane.delete("1.0", "end")
        textPane.config(state=DISABLED)

    def lockBoard() -> None:
        hexboardButtonA1.config(state=DISABLED)
        hexboardButtonB1.config(state=DISABLED)
        hexboardButtonC1.config(state=DISABLED)
        hexboardButtonA2.config(state=DISABLED)
        hexboardButtonB2.config(state=DISABLED)
        hexboardButtonC2.config(state=DISABLED)
        hexboardButtonA3.config(state=DISABLED)
        hexboardButtonB3.config(state=DISABLED)
        hexboardButtonC3.config(state=DISABLED)

    def unlockBoard() -> None:
        hexboardButtonA1.config(state=NORMAL)
        hexboardButtonB1.config(state=NORMAL)
        hexboardButtonC1.config(state=NORMAL)
        hexboardButtonA2.config(state=NORMAL)
        hexboardButtonB2.config(state=NORMAL)
        hexboardButtonC2.config(state=NORMAL)
        hexboardButtonA3.config(state=NORMAL)
        hexboardButtonB3.config(state=NORMAL)
        hexboardButtonC3.config(state=NORMAL)
    
    def moveSpace(target) -> None:
        sX, sY = returnCoords(sourceSpace.get())
        tX, tY = returnCoords(target)
        boardData.overwriteAndMove(sX, sY, tX, tY)
        updateGUIBoard()
        post(f"Player: {sourceSpace.get()} -> {target}")
        if checkEndGame(boardData):
            post("Player Wins\n")
            lockBoard()
            if learningBool.get(): ai.learnFromGame(False)
            ai.flushArchive()
        else:
            aiMove = ai.recordAndPickMove(boardData.returnCaptureString())
            aiS = aiMove[0]
            aiT = aiMove[1]
            handleAIMove(aiMove, boardData)
            updateGUIBoard()
            post(f"   CPU: {aiS} -> {aiT}")
            if checkEndGame(boardData):
                post("CPU Wins\n")
                lockBoard()
                if learningBool.get(): ai.learnFromGame(True)
                ai.flushArchive()

    def moveToA1() -> None: moveSpace("A1")
    def moveToB1() -> None: moveSpace("B1")
    def moveToC1() -> None: moveSpace("C1")
    def moveToA2() -> None: moveSpace("A2")
    def moveToB2() -> None: moveSpace("B2")
    def moveToC2() -> None: moveSpace("C2")

    def highlightSpace(spaceCoord: str) -> None:
        sourceSpace.set(spaceCoord)
        x, y = returnCoords(spaceCoord)
        moveSet = {
            "A1": ["X3", "X3", "X3"],
            "B1": ["X3", "X3", "X3"],
            "C1": ["X3", "X3", "X3"],
            "A2": ["X3", "A1", "B1"],
            "B2": ["A1", "B1", "C1"],
            "C2": ["B1", "C1", "X3"],
            "A3": ["X3", "A2", "B2"],
            "B3": ["A2", "B2", "C2"],
            "C3": ["B2", "C2", "X3"]
        }[spaceCoord]
        moveData = boardData.board[x][y].checkMoves(boardData)
        moveSet.append(spaceCoord)
        for i in range(3):
            if moveData[i] == False:
                moveSet[i] = "X3"
        lockBoard()
        if "A1" in moveSet:
            hexboardButtonA1.config(state=NORMAL)
            if spaceCoord == "A1": hexboardButtonA1.config(command=updateGUIBoard)
            else: hexboardButtonA1.config(command=moveToA1)
        if "B1" in moveSet:
            hexboardButtonB1.config(state=NORMAL)
            if spaceCoord == "B1": hexboardButtonB1.config(command=updateGUIBoard)
            else: hexboardButtonB1.config(command=moveToB1)
        if "C1" in moveSet:
            hexboardButtonC1.config(state=NORMAL)
            if spaceCoord == "C1": hexboardButtonC1.config(command=updateGUIBoard)
            else: hexboardButtonC1.config(command=moveToC1)
        if "A2" in moveSet:
            hexboardButtonA2.config(state=NORMAL)
            if spaceCoord == "A2": hexboardButtonA2.config(command=updateGUIBoard)
            else: hexboardButtonA2.config(command=moveToA2)
        if "B2" in moveSet:
            hexboardButtonB2.config(state=NORMAL)
            if spaceCoord == "B2": hexboardButtonB2.config(command=updateGUIBoard)
            else: hexboardButtonB2.config(command=moveToB2)
        if "C2" in moveSet:
            hexboardButtonC2.config(state=NORMAL)
            if spaceCoord == "C2": hexboardButtonC2.config(command=updateGUIBoard)
            else: hexboardButtonC2.config(command=moveToC2)
        if "A3" in moveSet:
            hexboardButtonA3.config(state=NORMAL, command=updateGUIBoard)
        if "B3" in moveSet:
            hexboardButtonB3.config(state=NORMAL, command=updateGUIBoard)
        if "C3" in moveSet:
            hexboardButtonC3.config(state=NORMAL, command=updateGUIBoard)
    
    def highlightA1() -> None: highlightSpace("A1")
    def highlightB1() -> None: highlightSpace("B1")
    def highlightC1() -> None: highlightSpace("C1")
    def highlightA2() -> None: highlightSpace("A2")
    def highlightB2() -> None: highlightSpace("B2")
    def highlightC2() -> None: highlightSpace("C2")
    def highlightA3() -> None: highlightSpace("A3")
    def highlightB3() -> None: highlightSpace("B3")
    def highlightC3() -> None: highlightSpace("C3")

    def illegalSpace() -> None: post("Cannot access this space.")

    def updateGUIBoard() -> None:
        updateData = []
        for row in boardData.board:
            for square in row:
                if type(square) is WhitePawn: updateData.append((white_space, True))
                elif type(square) is BlackPawn: updateData.append((black_space, False))
                else: updateData.append((blank_space, False))

        hexboardButtonA1.config(image=updateData[0][0])
        if updateData[0][1]: hexboardButtonA1.config(command=highlightA1)
        else: hexboardButtonA1.config(command=illegalSpace)

        hexboardButtonB1.config(image=updateData[1][0])
        if updateData[1][1]: hexboardButtonB1.config(command=highlightB1)
        else: hexboardButtonB1.config(command=illegalSpace)

        hexboardButtonC1.config(image=updateData[2][0])
        if updateData[2][1]: hexboardButtonC1.config(command=highlightC1)
        else: hexboardButtonC1.config(command=illegalSpace)

        hexboardButtonA2.config(image=updateData[3][0])
        if updateData[3][1]: hexboardButtonA2.config(command=highlightA2)
        else: hexboardButtonA2.config(command=illegalSpace)

        hexboardButtonB2.config(image=updateData[4][0])
        if updateData[4][1]: hexboardButtonB2.config(command=highlightB2)
        else: hexboardButtonB2.config(command=illegalSpace)

        hexboardButtonC2.config(image=updateData[5][0])
        if updateData[5][1]: hexboardButtonC2.config(command=highlightC2)
        else: hexboardButtonC2.config(command=illegalSpace)

        hexboardButtonA3.config(image=updateData[6][0])
        if updateData[6][1]: hexboardButtonA3.config(command=highlightA3)
        else: hexboardButtonA3.config(command=illegalSpace)

        hexboardButtonB3.config(image=updateData[7][0])
        if updateData[7][1]: hexboardButtonB3.config(command=highlightB3)
        else: hexboardButtonB3.config(command=illegalSpace)

        hexboardButtonC3.config(image=updateData[8][0])
        if updateData[8][1]: hexboardButtonC3.config(command=highlightC3)
        else: hexboardButtonC3.config(command=illegalSpace)

        unlockBoard()
    
    def resetBoard() -> None:
        boardData.reset()
        updateGUIBoard()
    
    def toggleLearn() -> None:
        if learningBool.get():
            learningBool.set(False)
            learnButton.config(text="Learn OFF")
        else:
            learningBool.set(True)
            learnButton.config(text="Learn ON")
        
    def confirmReset() -> None:
        branch = Tk()
        branch.title("Confirm Reset")
        branch.geometry("325x210")

        subWin = Frame(branch)
        subWin.pack(fill=BOTH, expand=1)

        def doReset() -> None:
            resetBoard()
            ai.reset()
            clearTextPane()
            branch.destroy()

        warningTitle = Label(subWin, text=" Are you sure you want to reset this AI? ", bg="#000", fg="#fff", font=("Calibri", 14))
        warningTitle.pack(pady=10)
        warningDesc = Label(subWin, text="Resetting will restore this AI to default settings and remove all collected data. Once reset, this AI cannot be restored unless it has already been saved externally.", wraplength=310)
        warningDesc.pack()
        confirmButton = Button(subWin, text="Yes, reset this AI.", width=40, command=doReset)
        confirmButton.pack(pady=5)
        cancelButton = Button(subWin, text="Cancel", height=2, width=28, font=("Calibri", 14), command=branch.destroy)
        cancelButton.pack()

        branch.mainloop()

    def openTrainMenu() -> None:
        branch = Tk()
        branch.title("Training Menu")
        branch.geometry("250x350")

        subWin = Frame(branch)
        subWin.pack(fill=BOTH, expand=1)

        save = BooleanVar()
        save.set(False)
        def invertSave(): save.set(not save.get())
        summary = BooleanVar()
        summary.set(False)
        def invertSummary(): summary.set(not summary.get())
        benchmark = BooleanVar()
        benchmark.set(False)
        def invertBenchmark(): benchmark.set(not benchmark.get())
        commentary = BooleanVar()
        commentary.set(False)
        def invertCommentary(): commentary.set(not commentary.get())
        log = BooleanVar()
        log.set(False)
        def invertLog(): log.set(not log.get())

        def startTraining() -> None:
            gameQuantityData = gameQuantityEntry.get()
            try:
                games = int(gameQuantityData)
                if games <= 0: raise ValueError()
            except ValueError:
                gameQuantityEntry.config(bg="#faa",fg="#000")
            else:
                startButton.config(text="Training...")
                startButton.config(state=DISABLED)
                closeButton.config(state=DISABLED)

                saveVal = save.get()
                summaryVal = summary.get()
                benchmarkVal = benchmark.get()
                commentaryVal = commentary.get()
                logVal = log.get()

                if logVal: logName = strftime("Training Log %d-%m-%Y %H-%M-%S.hexlog")
                else: logName = None
                virtualiseGames(ai, games, True, commentaryVal, logName)
                if saveVal: saveAI()
                if benchmarkVal: ai.plotBenchmarkHistory()

                branch.destroy()

        xOff, yOff = (10,10)
        buttonFooterX, buttonFooterY = (12,250)

        gameQuantityLabel = Label(subWin, text="No. of Games")
        gameQuantityEntry = Entry(subWin)

        configSave = Checkbutton(subWin, text="Save AI when done", variable=save, command=invertSave)
        dataConfigLabel = Label(subWin, text="Data Options")
        configSummary = Checkbutton(subWin, text="Open Summary when Done", variable=summary, command=invertSummary)
        configBenchmark = Checkbutton(subWin, text="Show Benchmark Progression*", variable=benchmark, command=invertBenchmark)
        logConfigLabel = Label(subWin, text="Logging Options")
        configCommentary = Checkbutton(subWin, text="Output Game info to Console", variable=commentary, command=invertCommentary)
        configLog = Checkbutton(subWin, text="Create training log (.hexlog)", variable=log, command=invertLog)
        noticeLabel = Label(subWin, text="*Matplotlib and Numpy required", fg="#888", font=("Calibri", 8))

        startButton = Button(subWin, text="START", width=18, height=1, font=("Calibri", 18), command=startTraining)
        closeButton = Button(subWin, text="Close", width=27, font=("Calibri", 12), command=branch.destroy)

        gameQuantityLabel.place(x=xOff, y=yOff)
        gameQuantityEntry.place(x=xOff, y=yOff+20)
        configSave.place(x=xOff, y=yOff+50)
        dataConfigLabel.place(x=xOff, y=yOff+80)
        configSummary.place(x=xOff, y=yOff+100)
        configBenchmark.place(x=xOff, y=yOff+120)
        logConfigLabel.place(x=xOff, y=yOff+150)
        configCommentary.place(x=xOff, y=yOff+170)
        configLog.place(x=xOff, y=yOff+190)
        noticeLabel.place(x=xOff, y=yOff+215)
        startButton.place(x=buttonFooterX,y=buttonFooterY)
        closeButton.place(x=buttonFooterX,y=buttonFooterY+60)

        if not chartsAvailable: configBenchmark.config(state=DISABLED)

        branch.mainloop()

    def openTestMenu() -> None:
        branch = Tk()
        branch.title("Test Menu")
        branch.geometry("250x235")

        subWin = Frame(branch)
        subWin.pack(fill=BOTH, expand=1)

        summary = BooleanVar()
        summary.set(False)
        def invertSummary(): summary.set(not summary.get())
        commentary = BooleanVar()
        commentary.set(False)
        def invertCommentary(): commentary.set(not commentary.get())
        log = BooleanVar()
        log.set(False)
        def invertLog(): log.set(not log.get())

        def startTesting() -> None:
            gameQuantityData = gameQuantityEntry.get()
            try:
                games = int(gameQuantityData)
                if games <= 0: raise ValueError()
            except ValueError:
                gameQuantityEntry.config(bg="#faa",fg="#000")
            else:
                startButton.config(text="Testing...")
                startButton.config(state=DISABLED)
                closeButton.config(state=DISABLED)

                commentaryVal = commentary.get()
                logVal = log.get()

                if logVal: logName = strftime("Test Log %d-%m-%Y %H-%M-%S.hexlog")
                else: logName = None
                virtualiseGames(ai, games, False, commentaryVal, logName)
                ai.plotWinsOverGames()

                branch.destroy()

        xOff, yOff = (10,10)
        buttonFooterX, buttonFooterY = (12,135)

        gameQuantityLabel = Label(subWin, text="No. of Games")
        gameQuantityEntry = Entry(subWin)

        logConfigLabel = Label(subWin, text="Logging Options")
        configCommentary = Checkbutton(subWin, text="Output Game info to Console", variable=commentary, command=invertCommentary)
        configLog = Checkbutton(subWin, text="Create testing log (.hexlog)", variable=log, command=invertLog)

        startButton = Button(subWin, text="START", width=18, height=1, font=("Calibri", 18), command=startTesting)
        closeButton = Button(subWin, text="Close", width=27, font=("Calibri", 12), command=branch.destroy)

        gameQuantityLabel.place(x=xOff, y=yOff)
        gameQuantityEntry.place(x=xOff, y=yOff+20)
        logConfigLabel.place(x=xOff, y=yOff+50)
        configCommentary.place(x=xOff, y=yOff+70)
        configLog.place(x=xOff, y=yOff+90)
        startButton.place(x=buttonFooterX,y=buttonFooterY)
        closeButton.place(x=buttonFooterX,y=buttonFooterY+60)

        branch.mainloop()

    def openBenchmark() -> None:
        branch = Tk()
        branch.title("Benchmark Score")
        branch.geometry("200x275")

        def openProgress() -> None: ai.plotBenchmarkHistory()

        subWin = Frame(branch)
        subWin.pack(fill=BOTH, expand=1)

        title = Label(subWin, text="Benchmark Score", font=("Calibri", 18))
        title.pack(pady=2)
        scoreDisplay = Label(subWin, text="0000", bg="#000", fg="#fff", height=1, width=6, font=("Calibri", 36))
        scoreDisplay.pack(pady=10)
        Label(subWin).pack()
        progressButton = Button(subWin, text="View Progress", width=16, font=("Calibri", 14), command=openProgress)
        progressButton.pack(pady=5)
        progressButton = Button(subWin, text="Close", width=23, font=("Calibri", 10), command=branch.destroy)
        progressButton.pack(pady=5)

        scoreDisplay.config(text=str(ai.benchmarkScore))

        branch.mainloop()

    def editLearnFactor() -> None:
        branch = Tk()
        branch.title("Change Learn Factor")
        branch.geometry("300x150")

        subWin = Frame(branch)
        subWin.pack(fill=BOTH, expand=1)

        def changeLearnFactor() -> None:
            data = numberEntry.get()
            try:
                newFactor = float(data)
                if newFactor <= 0 or newFactor > 1: raise ValueError()
            except ValueError:
                numberEntry.config(bg="#faa", fg="#000")
            else:
                ai.learnFactor = newFactor
                branch.destroy()

        title = Label(subWin, text="Change Learn Factor to:")
        title.pack(pady=10)
        numberEntry = Entry(subWin)
        numberEntry.pack()
        notice = Label(subWin, text="(Must be above 0 and must not exceed 1)", font=("Calibri", 8))
        notice.pack(pady=10)
        enterButton = Button(subWin, text="Confirm", width=8, command=changeLearnFactor)
        enterButton.place(x=150, y=115)
        closeButton = Button(subWin, text="Cancel", width=8, command=branch.destroy)
        closeButton.place(x=225, y=115)

        branch.mainloop()
    
    def changeInterface() -> None:
        root.withdraw()
        print("To return to the GUI, press Ctrl+C and re-run the program.")
        learn = learningBool.get()
        while True:
            boardData.reset()
            gameCycle(boardData, ai, learn)

    def openCustomiseMenu() -> None:
        branch = Tk()
        branch.title("Customise Window")
        branch.geometry("450x300")

        subWin = Frame(branch)
        subWin.pack(fill=BOTH, expand=1)

        def applyChanges() -> None:
            textPane.config(bg=textWindowEntry.get())
            textPane.config(foreground=textWinTextEntry.get())
            win.config(bg=bgColorEntry.get())
            resetButton.config(bg=bgColorEntry.get())
            resetButton.config(fg=textColorEntry.get())
            learnButton.config(bg=bgColorEntry.get())
            learnButton.config(fg=textColorEntry.get())
        
        def applyAndExit() -> None:
            applyChanges()
            branch.destroy()

        xOff, yOff = (10,10)
        buttonFooterX, buttonFooterY = (140,260)

        bgColorLabel = Label(subWin, text="Background Color")
        bgColorEntry = Entry(subWin)

        textColorLabel = Label(subWin, text="Text Color")
        textColorEntry = Entry(subWin)

        textWindowLabel = Label(subWin, text="Text Win. Background")
        textWindowEntry = Entry(subWin)

        textWinTextLabel = Label(subWin, text="Text Win. Text")
        textWinTextEntry = Entry(subWin)

        okButton = Button(subWin, text="OK", width=12, command=applyAndExit)
        applyButton = Button(subWin, text="Apply", width=12, command=applyChanges)
        closeButton = Button(subWin, text="Close", width=12, command=branch.destroy)

        bgColorLabel.place(x=xOff, y=yOff)
        bgColorEntry.place(x=xOff, y=yOff+20)
        textColorLabel.place(x=xOff+150, y=yOff)
        textColorEntry.place(x=xOff+150, y=yOff+20)
        textWindowLabel.place(x=xOff, y=yOff+50)
        textWindowEntry.place(x=xOff, y=yOff+70)
        textWinTextLabel.place(x=xOff+150, y=yOff+50)
        textWinTextEntry.place(x=xOff+150, y=yOff+70)
        okButton.place(x=buttonFooterX, y=buttonFooterY)
        applyButton.place(x=buttonFooterX+100, y=buttonFooterY)
        closeButton.place(x=buttonFooterX+200, y=buttonFooterY)

        branch.mainloop()

    def saveAI() -> None:
        filename = filedialog.asksaveasfilename(defaultextension=".hexai", filetypes=[("Hexapywn AI", "*.hexai")])
        try: ai.exportAI(filename)
        except FileNotFoundError:
            if filename != "": post("[!] Error while Saving AI\n")
    
    def loadAI() -> None:
        filename = filedialog.askopenfilename(defaultextension=".hexai", filetypes=[("Hexapywn AI", "*.hexai")])
        try: ai.importAI(filename)
        except FileNotFoundError:
            if filename != "": post("[!] File not Found!\n")
        else: post("[*] AI loaded from file.\n")

    root = Tk()
    root.title("Hexapywn.py (Local AI)")
    root.geometry("600x400")

    win = Frame(root)
    win.pack(fill=BOTH, expand=1)

    menu = Menu(root)
    root.config(menu=menu)

    fileMenu = Menu(menu)
    menu.add_cascade(label='File', menu=fileMenu)
    fileMenu.add_command(label="Save AI as...", command=saveAI)
    fileMenu.add_command(label="Import Data...", command=loadAI)
    fileMenu.add_command(label="Reset Current", command=confirmReset)
    fileMenu.add_separator()
    fileMenu.add_command(label="Clear Text Pane", command=clearTextPane)
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit App", command=root.destroy)

    trainMenu = Menu(menu)
    menu.add_cascade(label='Configure', menu=trainMenu)
    trainMenu.add_command(label="Train AI", command=openTrainMenu)
    trainMenu.add_command(label="Benchmark AI", command=openBenchmark)
    trainMenu.add_command(label="Test AI", command=openTestMenu)

    advancedMenu = Menu(menu)
    menu.add_cascade(label='Advanced', menu=advancedMenu)
    advancedMenu.add_command(label='Adjust Learn Factor', command=editLearnFactor)
    advancedMenu.add_command(label='Switch to Console Mode', command=changeInterface)
    advancedMenu.add_separator()
    advancedMenu.add_command(label='UI Preferences', command=openCustomiseMenu)

    textPane = Text(win, width=28, height=23, state=DISABLED)
    textPane.place(x=10,y=10)

    blank_space = PhotoImage(file=r".\assets\blankUI.png")
    white_space = PhotoImage(file=r".\assets\whiteUI.png")
    black_space = PhotoImage(file=r".\assets\blackUI.png")

    boardPosX, boardPosY = (265,20)

    hexboardButtonA1 = Button(win, image=black_space)
    hexboardButtonA2 = Button(win, image=blank_space)
    hexboardButtonA3 = Button(win, image=white_space)
    hexboardButtonB1 = Button(win, image=black_space)
    hexboardButtonB2 = Button(win, image=blank_space)
    hexboardButtonB3 = Button(win, image=white_space)
    hexboardButtonC1 = Button(win, image=black_space)
    hexboardButtonC2 = Button(win, image=blank_space)
    hexboardButtonC3 = Button(win, image=white_space)

    imageTuple = (blank_space, black_space, white_space)

    hexboardButtonA1.config(command=None)
    hexboardButtonA2.config(command=None)
    hexboardButtonA3.config(command=None)
    hexboardButtonB1.config(command=None)
    hexboardButtonB2.config(command=None)
    hexboardButtonB3.config(command=None)
    hexboardButtonC1.config(command=None)
    hexboardButtonC2.config(command=None)
    hexboardButtonC3.config(command=None)

    hexboardButtonA1.place(x=boardPosX, y=boardPosY)
    hexboardButtonA2.place(x=boardPosX, y=boardPosY+105)
    hexboardButtonA3.place(x=boardPosX, y=boardPosY+210)
    hexboardButtonB1.place(x=boardPosX+105, y=boardPosY)
    hexboardButtonB2.place(x=boardPosX+105, y=boardPosY+105)
    hexboardButtonB3.place(x=boardPosX+105, y=boardPosY+210)
    hexboardButtonC1.place(x=boardPosX+210, y=boardPosY)
    hexboardButtonC2.place(x=boardPosX+210, y=boardPosY+105)
    hexboardButtonC3.place(x=boardPosX+210, y=boardPosY+210)

    resetButton = Button(win, text='RESET', width=9, font=("Calibri", 14), command=resetBoard)
    resetButton.place(x=265, y=350)

    learnButton = Button(win, text='Learn ON', width=9, font=("Calibri", 14), command=toggleLearn)
    learningBool = BooleanVar()
    learningBool.set(True)
    learnButton.place(x=480, y=350)

    sourceSpace = StringVar()

    post("[*] Local AI Ready.\n")
    updateGUIBoard()
    root.mainloop()

def main() -> None:
    initialiseUI()

if __name__ == "__main__": main()