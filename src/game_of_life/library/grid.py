"""Parse image into an array of arrays."""

from PIL import Image
import numpy as np


class Grid:
    """Collection of cells that make up an image."""

    def __init__(self, starting_board_file: str):
        """Parse board from starting position and v/h wormholes."""
        # Initial board state
        self.starting_board_file = starting_board_file
        self.img = Image.open(starting_board_file).convert("RGB")
        self.width, self.height = self.img.size
        self.data = np.asarray(self.img, dtype="int32")
        self.default_board = self._get_board()
        self.board = self.default_board

        # neighbor mapping
        self.default_neighbor_map = self._map_neighbors()
        self.neighbor_map = self.default_neighbor_map

        # debug
        self._debug = False
        self.frames = [self.board]

    @property
    def debug(self) -> bool:
        """Debug mode."""
        return self._debug

    @debug.setter
    def debug(self, dbg: bool = False) -> None:
        """Debug mode setter."""
        if not isinstance(dbg, bool):
            raise ValueError("Debug must be boolean")
        self._debug = dbg

    def reset(self) -> None:
        """Reset board to starting position."""
        self.board = self.default_board

    def validate_coords(self, row: int, col: int) -> bool:
        """Validate a set of coordinates is within the bounds of this board."""
        return 0 <= row < self.height and 0 <= col < self.width

    def _get_board(self) -> list[list[int]]:
        """Create bitmap from initial state."""
        board = np.zeros((self.height, self.width), dtype=bool)

        for row in range(self.height):
            if row == 4:
                breakpoint()
            for col in range(self.width):
                # Check if pixel is white (alive)
                if np.all(self.data[row, col] == [255, 255, 255]):
                    board[row, col] = True
        return board

    def _map_neighbors(self) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """Create coordinate map of all cell neighbors."""
        neighbor_map = {}
        for row in range(self.height):
            for col in range(self.width):
                actual_neighbors = []
                for row_delta in [-1, 0, 1]:
                    for col_delta in [-1, 0, 1]:
                        if row_delta == col_delta == 0:
                            continue
                        # check each cell in a 3x3 grid including current cell
                        row_neighbor = row + row_delta
                        col_neighbor = col + col_delta
                        if self.validate_coords(row_neighbor, col_neighbor):
                            # only bother checking if neighbor coords are within board
                            actual_neighbors.append((row_neighbor, col_neighbor))
                neighbor_map[(row, col)] = actual_neighbors
        return neighbor_map

    def _count_live_neighbors(self, row: int, col: int) -> int:
        """Count live neighbors for a cell using the neighbor map"""
        count = 0
        for nr, nc in self.neighbor_map.get((row, col), []):
            if self.board[nr, nc]:
                count += 1
        return count

    def step(self) -> None:
        """Perform one iteration of the Game of Life"""
        new_board = np.zeros_like(self.board)

        for row in range(self.height):
            for col in range(self.width):
                live_neighbors = self._count_live_neighbors(row, col)
                current_state = self.board[row, col]

                # Apply Conway's rules
                if current_state:
                    if live_neighbors < 2:
                        # Dies by underpopulation
                        new_board[row, col] = False
                    elif live_neighbors in [2, 3]:
                        # Lives on
                        new_board[row, col] = True
                    else:
                        # Dies by overpopulation
                        new_board[row, col] = False
                else:
                    if live_neighbors == 3:
                        # Becomes alive by reproduction
                        new_board[row, col] = True

        self.board = new_board
        if self.debug:
            self.frames.append(new_board)

    def export_board(self, file_name: str) -> None:
        """Save board state to file."""
        img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Set white for live cells, black for dead cells
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col]:
                    img_array[row, col] = [255, 255, 255]
                else:
                    img_array[row, col] = [0, 0, 0]

        img = Image.fromarray(img_array)
        img.save(file_name)
