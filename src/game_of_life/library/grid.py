"""Parse image into an array of arrays."""

from PIL import Image
import numpy as np
from collections import defaultdict


class Grid:
    """Collection of cells that make up an image."""

    def __init__(self, starting_board_file: str, v_wormholes: str, h_wormholes: str):
        """Parse board from starting position and v/h wormholes."""
        # Initial board state
        self.starting_board_file = starting_board_file
        self.img = Image.open(starting_board_file).convert("RGB")
        self.width, self.height = self.img.size
        self.data = np.asarray(self.img, dtype="int32")
        self.board = self._get_board()

        # wormholes
        self.v_wh_img = Image.open(v_wormholes).convert("RGB")
        self.v_wormholes = self._parse_wormholes(
            pixels=np.asarray(self.v_wh_img, dtype="int32")
        )
        self.h_wh_img = Image.open(h_wormholes).convert("RGB")
        self.h_wormholes = self._parse_wormholes(
            pixels=np.asarray(self.h_wh_img, dtype="int32")
        )

        # neighbor mapping
        self.neighbor_map = self._map_neighbors()

    def _get_board(self) -> list[list[int]]:
        """Create bitmap from initial state."""
        board = np.zeros((self.height, self.width), dtype=bool)

        for row in range(self.height):
            for col in range(self.width):
                # Check if pixel is white (alive)
                if np.all(self.data[row, col] == [255, 255, 255]):
                    board[row, col] = True
        return board

    def _parse_wormholes(
        self, pixels: np.ndarray
    ) -> dict[tuple[int, int], tuple[int, int]]:
        """Parse wormhole connections from tunnel bitmap."""
        wormholes = {}
        color_positions = defaultdict(list)

        # Group positions by color
        for row in range(self.height):
            for col in range(self.width):
                color = tuple(pixels[row, col])
                # Skip black pixels (no wormhole)
                if color != (0, 0, 0):
                    color_positions[color].append((row, col))

        # Create bidirectional wormhole connections
        for color, positions in color_positions.items():
            if len(positions) == 2:
                pos1, pos2 = positions
                wormholes[pos1] = pos2
                wormholes[pos2] = pos1
            elif len(positions) > 2:
                print(
                    f"Warning: Color {color} has {len(positions)} positions, expected 2"
                )

        return wormholes

    def _get_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        """Get cell neighbors based on board dimensions."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbors.append((nr, nc))
        return neighbors

    def _map_neighbors(self) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """Create coordinate map of all cell neighbors."""
        neighbor_map = {}
        for row in range(self.height):
            for col in range(self.width):
                default_neighbors = self._get_neighbors(row, col)
                neighbor_map[(row, col)] = default_neighbors
        return neighbor_map

    def _apply_wormhole_transform(
        self, row: int, col: int, dr: int, dc: int
    ) -> tuple[int, int] | None:
        """Apply wormhole transformation to a cell's neighbor."""
        # Standard neighbor position
        neighbor_row, neighbor_col = row + dr, col + dc

        # Check bounds
        if not (0 <= neighbor_row < self.height and 0 <= neighbor_col < self.width):
            return None

        # Determine wormhole precedence: top > right > bottom > left
        wormhole_source = None

        # Check for wormholes in precedence order
        if dr < 0:  # top direction
            if (row, col) in self.v_wormholes:
                wormhole_source = "vertical"
        elif dc > 0:  # right direction
            if (row, col) in self.h_wormholes:
                wormhole_source = "horizontal"
        elif dr > 0:  # bottom direction
            if (row, col) in self.v_wormholes:
                wormhole_source = "vertical"
        elif dc < 0:  # left direction
            if (row, col) in self.h_wormholes:
                wormhole_source = "horizontal"

        # Apply wormhole transformation if applicable
        if wormhole_source == "horizontal" and (row, col) in self.h_wormholes:
            partner_row, partner_col = self.h_wormholes[(row, col)]
            return partner_row + dr, partner_col + dc
        elif wormhole_source == "vertical" and (row, col) in self.v_wormholes:
            partner_row, partner_col = self.v_wormholes[(row, col)]
            return partner_row + dr, partner_col + dc

        return neighbor_row, neighbor_col

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
