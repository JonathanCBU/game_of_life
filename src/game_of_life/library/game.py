#!/usr/bin/env python3
"""
Conway's Game of Life with Wormholes
Implementation for the coding assignment

This program simulates Conway's Game of Life with the addition of wormhole tunnels
that connect distant parts of the grid, allowing non-local interactions.
"""

import numpy as np
from PIL import Image
import os
import sys
from typing import Dict, Tuple, Set, List
from collections import defaultdict


class WormholeGameOfLife:
    def __init__(self, input_dir: str):
        """
        Initialize the Game of Life with Wormholes
        
        Args:
            input_dir: Directory containing input PNG files
        """
        self.input_dir = input_dir
        self.board = None
        self.height = 0
        self.width = 0
        self.neighbor_map = {}  # Maps (row, col) -> list of neighbor coordinates
        
        # Load input files
        self._load_starting_position()
        self._load_wormhole_tunnels()
        self._build_neighbor_map()
    
    def _load_starting_position(self):
        """Load the initial board state from starting_position.png"""
        img_path = os.path.join(self.input_dir, 'starting_position.png')
        img = Image.open(img_path).convert('RGB')
        
        self.width, self.height = img.size
        self.board = np.zeros((self.height, self.width), dtype=bool)
        
        # Convert image to board state (white = alive, black = dead)
        pixels = np.array(img)
        for row in range(self.height):
            for col in range(self.width):
                # Check if pixel is white (alive)
                if np.all(pixels[row, col] == [255, 255, 255]):
                    self.board[row, col] = True
    
    def _load_wormhole_tunnels(self):
        """Load and parse horizontal and vertical tunnel maps"""
        # Load horizontal tunnels
        h_tunnel_path = os.path.join(self.input_dir, 'horizontal_tunnel.png')
        h_img = Image.open(h_tunnel_path).convert('RGB')
        h_pixels = np.array(h_img)
        
        # Load vertical tunnels
        v_tunnel_path = os.path.join(self.input_dir, 'vertical_tunnel.png')
        v_img = Image.open(v_tunnel_path).convert('RGB')
        v_pixels = np.array(v_img)
        
        # Parse wormhole connections
        self.h_wormholes = self._parse_wormholes(h_pixels, 'horizontal')
        self.v_wormholes = self._parse_wormholes(v_pixels, 'vertical')
    
    def _parse_wormholes(self, pixels: np.ndarray, orientation: str) -> Dict[Tuple[int, int], Tuple[int, int]]:
        """
        Parse wormhole connections from tunnel bitmap
        
        Args:
            pixels: RGB pixel array
            orientation: 'horizontal' or 'vertical'
            
        Returns:
            Dictionary mapping coordinates to their wormhole partner
        """
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
                print(f"Warning: Color {color} has {len(positions)} positions, expected 2")
        
        return wormholes
    
    def _get_standard_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get the 8 standard neighbors of a cell"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbors.append((nr, nc))
        return neighbors
    
    def _apply_wormhole_transform(self, row: int, col: int, dr: int, dc: int) -> Tuple[int, int]:
        """
        Apply wormhole transformation to a neighbor offset
        
        Args:
            row, col: Current cell position
            dr, dc: Neighbor offset
            
        Returns:
            Transformed neighbor coordinates
        """
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
                wormhole_source = 'vertical'
        elif dc > 0:  # right direction
            if (row, col) in self.h_wormholes:
                wormhole_source = 'horizontal'
        elif dr > 0:  # bottom direction
            if (row, col) in self.v_wormholes:
                wormhole_source = 'vertical'
        elif dc < 0:  # left direction
            if (row, col) in self.h_wormholes:
                wormhole_source = 'horizontal'
        
        # Apply wormhole transformation if applicable
        if wormhole_source == 'horizontal' and (row, col) in self.h_wormholes:
            partner_row, partner_col = self.h_wormholes[(row, col)]
            return partner_row + dr, partner_col + dc
        elif wormhole_source == 'vertical' and (row, col) in self.v_wormholes:
            partner_row, partner_col = self.v_wormholes[(row, col)]
            return partner_row + dr, partner_col + dc
        
        return neighbor_row, neighbor_col
    
    def _build_neighbor_map(self):
        """Build a complete neighbor map for all cells considering wormholes"""
        for row in range(self.height):
            for col in range(self.width):
                neighbors = []
                
                # Check all 8 directions
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        
                        # Get neighbor with wormhole transformation
                        neighbor_pos = self._apply_wormhole_transform(row, col, dr, dc)
                        
                        if neighbor_pos is not None:
                            nr, nc = neighbor_pos
                            if 0 <= nr < self.height and 0 <= nc < self.width:
                                neighbors.append((nr, nc))
                
                self.neighbor_map[(row, col)] = neighbors
    
    def _count_live_neighbors(self, row: int, col: int) -> int:
        """Count live neighbors for a cell using the neighbor map"""
        count = 0
        for nr, nc in self.neighbor_map.get((row, col), []):
            if self.board[nr, nc]:
                count += 1
        return count
    
    def step(self):
        """Perform one iteration of the Game of Life"""
        new_board = np.zeros_like(self.board)
        
        for row in range(self.height):
            for col in range(self.width):
                live_neighbors = self._count_live_neighbors(row, col)
                current_state = self.board[row, col]
                
                # Apply Conway's rules
                if current_state:  # Live cell
                    if live_neighbors < 2:
                        new_board[row, col] = False  # Dies by underpopulation
                    elif live_neighbors in [2, 3]:
                        new_board[row, col] = True   # Lives on
                    else:
                        new_board[row, col] = False  # Dies by overpopulation
                else:  # Dead cell
                    if live_neighbors == 3:
                        new_board[row, col] = True   # Becomes alive by reproduction
        
        self.board = new_board
    
    def save_state(self, filename: str):
        """Save current board state as PNG image"""
        img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Set white for live cells, black for dead cells
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col]:
                    img_array[row, col] = [255, 255, 255]  # White
                else:
                    img_array[row, col] = [0, 0, 0]        # Black
        
        img = Image.fromarray(img_array)
        img.save(os.path.join(self.input_dir, filename))
    
    def simulate(self, iterations: List[int]):
        """
        Run simulation and save states at specified iterations
        
        Args:
            iterations: List of iteration numbers to save (e.g., [1, 10, 100, 1000])
        """
        current_iteration = 0
        iteration_set = set(iterations)
        
        print(f"Starting simulation for {max(iterations)} iterations...")
        
        for target_iteration in range(1, max(iterations) + 1):
            self.step()
            current_iteration += 1
            
            if current_iteration in iteration_set:
                filename = f"{current_iteration}.png"
                self.save_state(filename)
                print(f"Saved state after {current_iteration} iterations: {filename}")
    
    def create_animation_frames(self, max_iterations: int = 100):
        """Create frames for animation debugging (optional)"""
        frames = []
        
        # Save initial state
        img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col]:
                    img_array[row, col] = [255, 255, 255]
        frames.append(Image.fromarray(img_array))
        
        # Generate frames
        for i in range(max_iterations):
            self.step()
            img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            for row in range(self.height):
                for col in range(self.width):
                    if self.board[row, col]:
                        img_array[row, col] = [255, 255, 255]
            frames.append(Image.fromarray(img_array))
        
        # Save as GIF
        frames[0].save(
            os.path.join(self.input_dir, 'animation.gif'),
            save_all=True,
            append_images=frames[1:],
            duration=100,  # 100ms per frame
            loop=0
        )
        print(f"Animation saved: animation.gif")


def main():
    """Main function to run the simulation"""
    if len(sys.argv) != 2:
        print("Usage: python game_of_life_wormhole.py <input_directory>")
        print("Example: python game_of_life_wormhole.py example-1/")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    
    if not os.path.exists(input_dir):
        print(f"Error: Directory '{input_dir}' does not exist")
        sys.exit(1)
    
    # Check for required input files
    required_files = ['starting_position.png', 'horizontal_tunnel.png', 'vertical_tunnel.png']
    for filename in required_files:
        filepath = os.path.join(input_dir, filename)
        if not os.path.exists(filepath):
            print(f"Error: Required file '{filename}' not found in '{input_dir}'")
            sys.exit(1)
    
    try:
        # Initialize and run simulation
        game = WormholeGameOfLife(input_dir)
        
        # Run simulation for required iterations
        iterations_to_save = [1, 10, 100, 1000]
        game.simulate(iterations_to_save)
        
        # Optionally create animation for debugging
        # Uncomment the next line to generate animation frames
        # game.create_animation_frames(50)
        
        print("Simulation completed successfully!")
        
    except Exception as e:
        print(f"Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()