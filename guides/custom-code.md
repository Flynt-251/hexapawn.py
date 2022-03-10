# Guide for Developers

This is the root for anyone wishing to modify the code for their own use. Below is a set of contents and a summary of how the program works. Example code will also be added.

## Contents

(Coming Soon)

## Where to put your own code

There is a subroutine towards the end of the program called `main()`. This is where you should put code you want to execute. Before you do though, you need to remove the `initialiseUI()` code first. Here's what it should look like:

```python
def main() -> None:
    # Put your code here
```

## Classes

This project utilises Object-Oriented Programming (OOP), below is a basic outline of each class used:

### Pawn

Has two children: `BlackPawn` and `WhitePawn`

Each pawn created has its own position assigned to it, which should be based off of its position on the board. They have methods to check where they can move and for actual movement.

### hexBoard

Short for "Hexapawn Board". Upon creation, a Hexapawn Board automatically creates a starting board with all of the necessary pawn objects. This board is a 2D list containing 3 sub-lists each with a length of three. You can move contents, reset and convert to a specialised string format (This is used by the machine learning algorithm).

### ComputerPlayer

Has one child: `MasterPlayer`

An AI that acts as the black player of the game. There are methods for learning, saving to files, resetting and plotting statistics using `matplotlib`.