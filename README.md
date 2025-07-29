Inspired from [GoL1](https://github.com/mwharrisjr/Game-of-Life) & [GoL2](https://github.com/Syntaf/GameOfLife) & [GoL3](https://github.com/duckythescientist/SmoothLife/tree/master)

Check them out for more theory and info.


# Conway's Game of Life

The Game of Life is a cellular automaton created by John H. Conway in 1970. The game is a zero-player game in which an initially configured 2D grid of cells evolves according to the Game of Life.

## Ruleset

Using the following ruleset the 2D grid of cells will evolve from generation to generation until it reaches a static state of either all dead cells or a mix of still, oscillating, or moving (spaceship) cells.

1. _**Underpopulation**_ - If a live cell has is surrounded by less than two surrounding neighbours it dies and does not make it to the next generation.
2. _**Equilibrium**_ - If a live cell is surrounded by two or three living neighbors the cell stays alive and makes it to the next generation.
3. _**Overpopulation**_ - If a live cell is surrounded by more than three living neighbors the cell dies and does not make it to the next generation.
4. _**Reproduction**_ - If a dead cell is surrounded by three living neighbors the cell stays alive and makes it to the next generation.
