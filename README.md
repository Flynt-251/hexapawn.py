# hexapawn.py

This is an old project of mine, where I took inspiration from Vsauce2's "Shreksapawn" video, where I created a hexapawn game, complete with reward-punishment based learning, file handling, benchmarking and a GUI. The video can be found [here](https://www.youtube.com/watch?v=sw7UAZNgGg8) if you're interested.

## What is Hexapawn?

Hexapawn was invented by Martin Gardner, who was a writer in Popular Mathematics. He focused on recreational maths and so as a writer, he would create games in his own column for *Scientific American*, titled "Mathematical Games". Hexapawn is just one of the many games he created.

In Hexapawn, you and another player (Typically, an AI) play on a 3x3 chess board, and you each have three pawns on your side of the board, in this configuration:

![Starting Layout](assets/readme-images/start%20grid.png)

Your pawn can move as it typically would in Chess, *except no pawn can move two spaces forward on its first move*. So, you can move forward one space if it is unoccupied, or diagonally to the left or right if there is an opponent piece there (you remove that opponent piece from play). You win the game by either:

- Capturing all your opponent's pieces;
- Getting one of your own pieces to the opposite side of the board or;
- Forcing your opponent into a state where they cannot move, by blocking their pieces.

## How does the AI learn?

In basic terms, the AI picks moves randomly. It changes its probabilites of picking each move as it learns how to play the game. It is learning by reducing the chance it picks a poor move and increasing the chance it picks a good move. This is a high-level explanation.

## How do I use the program?

Once you've cloned the repository and ran the app.py file, you should be greeted to this interface:

![UI for Windows](assets/readme-images/user-interface.png)

Try clicking on squares containing white pieces and then selecting where you want to move. You can click the same space again to de-select that piece. When a game ends, click 'RESET' to play another game. If you want the AI to stop learning from games, click "Learn ON". It should change to "Learn OFF". Click again to re-enable learning.

You should not be required to modify anything in the code to get this to work.

## Is there anything else I can do?

There are plenty of other tools available in this application. Below is a set of contents of guides for each of the drop-down menus on the GUI:

- [Save and Load AI](guides/saving-and-loading.md)
- [Training and Testing](guides/automate-games.md)
- [Advanced Options](guides/advanced-menu.md)
