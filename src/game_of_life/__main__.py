"""Main entry points for game of life."""

import argparse


def get_args() -> argparse.Namespace:
    """Command line args config."""
    parser = argparse.ArgumentParser(
        prog="game-of-life",
        description="Simulate Conway's game of life",
    )

    parser.add_argument(
        "-s", "--starting-positions", help="Absolute path to starting configuration"
    )


def main() -> None:
    """Calculate game results based on CLI."""
