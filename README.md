# game_of_life

## How to run

### Dependencies

__Dependencies may be installed manually into a virtual environment, or by using PDM if it is present on the machine running this code__

1. Python>=3.13
2. numpy>=2.2.6
2. pillow>=11.2.1

### \_\_main__.py

- To run the program, call `python3 <path_to_main>/__main__.py` from whatever Python environment your dependencies are installed in.

## Approach

Initially, my approach was to build the game of life vanilla, and then layer in the wormholes.

Initially, I planned to create a set of inheriting classes (Cell -> Row/Col -> Grid), but after a little time architecting that solution I realized that a mono-class grid made more sense.

Once I had a simple game of life Grid working, I put the coding aside to plan out how to handle wormholes.

After reading over the project description I singled out where the different holes in the explanation were. Mainly, I was not confident that I could predict what neighbors were observed by a cell based on what wormholes it is next to.

From the project description I concluded:

1. Wormholes "fold" the grid tso that the rows/columns of the wormholes match up
    - This means, if a cell is to the left of a horizontal wormhole, that cell's right-side neighbors will change to be the cells above, at, and below the wormhole exit (and vice-versa for being above/below a vertical wormhole)
2. If a cell is a wormhole, then all it's neighbors are those of the other wormhole boundary

While testing my solution against the example problems, I regularly got close-but-not-quite results. This was very frustrating, though thankfully my extensive debugging with pdb helped me fix a few other unforseen bugs.

## Use of AI

When writing the initial boilerplate code CoPilot and Claude were extremely helpful. Claude was able to present the logic needed for iterating over every cell and determining state, while CoPilot code completion made writing the code far faster than it used to be. Both of these are tools I use in my day-to-day, and applying them to the basic Game of Lif was very straightforward.

Once moving on to wormholes, Claude became less helpful due to the novelty of the problem, fortunately I know how to flag incorrect ideas from an LLM.


## Conclusion

I had a great time working on this project. Not only is the Game of Life a fascinating mathematical simulation, but the wormholes added an entirely new and fun dimenstion to things. Even in the event my solution is not fully correct or I missed a (literal) edge case, I am thankful for the opportunity to complete this project!

## What I would have improved

Given more time, I would have added:

1. Unit testing of simple grid operations like getting default neighbors, counting the number of surrounding live cells, and applying wormhole transforms on cell neighbor sets
2. CI/CD via github actions and ruff
3. A CLI (using argparse) and some pdm entry points for testing the code out more easily

