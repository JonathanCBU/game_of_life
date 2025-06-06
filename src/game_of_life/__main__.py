"""Main entry points for game of life."""

from library.grid import Grid
import os


def main() -> None:
    """Calculate game results."""
    current_path = os.path.dirname(os.path.abspath(__file__))
    parent_path = current_path.split("srcs")[0]
    for problem in range(1, 5):
        problem_dir = os.path.join(parent_path, f"problem-{problem}")
        grid = Grid(
            starting_board_file=os.path.join(problem_dir, "starting_position.png"),
            v_wormholes=os.path.join(problem_dir, "vertical_tunnel.png"),
            h_wormholes=os.path.join(problem_dir, "horizontal_tunnel.png"),
        )

        # apply normal wormhole transforms to each cell
        grid._wormhole_board()

        # handle cells that are wormholes separately
        grid._replace_wormhole_neighbors()

        for step_count in [1, 10, 100, 1000]:
            grid.reset()
            for _ in range(0, step_count):
                grid.step()
            grid.export_board(os.path.join(problem_dir, f"{step_count}.png"))


if __name__ == "__main__":
    main()
