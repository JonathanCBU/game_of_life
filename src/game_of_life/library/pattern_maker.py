"""Pattern generator for Game of Life starting frames."""

import numpy as np
from PIL import Image


class PatternMaker:
    """Generate images for starting frames."""

    def __init__(
        self,
        height: int,
        width: int,
        pattern: list[list[bool | int]],
        pattern_start: tuple[int, int] = (0, 0),
    ) -> None:
        """Assemble board from pattern."""
        self.height = height
        self.width = width
        self.pattern = pattern
        self.pattern_start = pattern_start
        self.board = self._assemble_board()

    def _assemble_board(self) -> list[list[int]]:
        """Create board of ints."""
        zeros = np.zeros((self.height, self.width), dtype=int)

        for r, row in enumerate(self.pattern):
            for c, col in enumerate(row):
                zeros[self.pattern_start[0] + r, self.pattern_start[1] + c] = int(col)

        return zeros

    def export_board(self, file_name: str) -> None:
        """Save board to file."""
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
