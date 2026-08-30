"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from importlib import machinery
from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile
from src.powerups.LineBomb import LineBomb
from src.powerups.ColorBomb import ColorBomb


class Board:
    def __init__(self, x: int, y: int, level: int = 1) -> None:
        self.x = x
        self.y = y
        self.level = level
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.render(surface, self.x, self.y)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        # Calculate how many colors are available based on the level.
        # Starts easy (fewer colors) and gets harder (more colors) up to NUM_COLORS
        num_colors_available = min(settings.NUM_COLORS, 5 + self.level)
        
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, num_colors_available - 1)
               
                while self._is_match_generated(i, j, color):
                    color = random.randint(0, num_colors_available - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

        # Ensure the board has at least one possible match
        if not self.has_possible_matches():
            self._initialize_tiles()

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile], simulate: bool = False
    ) -> Optional[List[List[Tile]]]:
        self.matches = []
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            
            if len(match) > 0:
                # PowerUp generation Logic
                if not simulate:
                    #Calculate max straight, because it can't be a match of 5 L-Shape for example
                    max_in_row = max(sum(1 for t in match if t.i == row_i) for row_i in set(t.i for t in match))
                    max_in_col = max(sum(1 for t in match if t.j == col_j) for col_j in set(t.j for t in match))
                    max_straight = max(max_in_row, max_in_col)

                    if max_straight == 4:
                        powerup = LineBomb(tile.i, tile.j, tile.color)
                        self.tiles[tile.i][tile.j] = powerup
                        
                        match = [t for t in match if not (t.i == tile.i and t.j == tile.j)]
                        
                    elif max_straight >= 5:
                        powerup = ColorBomb(tile.i, tile.j, tile.color)
                        self.tiles[tile.i][tile.j] = powerup
                        
                        match = [t for t in match if not (t.i == tile.i and t.j == tile.j)]
                
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self) -> None:
        # Collect all initial tiles to destroy
        tiles_to_destroy = []
        for match in self.matches:
            for tile in match:
                if tile not in tiles_to_destroy:
                    tiles_to_destroy.append(tile)
        
        # Process explosions (chain reactions)
        i = 0
        while i < len(tiles_to_destroy):
            tile = tiles_to_destroy[i]
            
            # Check if the actual tile is a bomb
            if getattr(tile, 'is_line_bomb', False) or getattr(tile, 'is_color_bomb', False):
                # Get the tiles to destroy
                targets = tile.get_explosion_targets(self)
                # Add them to the list of tiles to destroy
                for t in targets:
                    if t not in tiles_to_destroy:
                        tiles_to_destroy.append(t)
            
            i += 1
            
        # Remove them all from the board
        for tile in tiles_to_destroy:
            self.tiles[tile.i][tile.j] = None

        self.matches = []
        return tiles_to_destroy

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    # Same logic as initialize_tiles for difficulty scaling
                    num_colors_available = min(settings.NUM_COLORS, 5 + getattr(self, 'level', 1))
                    
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, num_colors_available - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def has_possible_matches(self) -> bool:
        # First, check if there's any powerup on the board.
        # If there is, the player can click it, so the board is not stuck.
        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    if getattr(tile, 'is_line_bomb', False) or getattr(tile, 'is_color_bomb', False):
                        return True

        # Check horizontal swaps
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH - 1):
                tile1 = self.tiles[i][j]
                tile2 = self.tiles[i][j + 1]

                # Swap temporarily
                self.tiles[i][j] = tile2
                self.tiles[i][j + 1] = tile1
                tile1.j = j + 1
                tile2.j = j

                matches = self.calculate_matches_for([tile1, tile2], simulate=True)
                self.matches = []

                # Revert swap
                self.tiles[i][j] = tile1
                self.tiles[i][j + 1] = tile2
                tile1.j = j
                tile2.j = j + 1

                if matches is not None:
                    return True

        # Check vertical swaps
        for i in range(settings.BOARD_HEIGHT - 1):
            for j in range(settings.BOARD_WIDTH):
                tile1 = self.tiles[i][j]
                tile2 = self.tiles[i + 1][j]

                # Swap temporarily
                self.tiles[i][j] = tile2
                self.tiles[i + 1][j] = tile1
                tile1.i = i + 1
                tile2.i = i

                matches = self.calculate_matches_for([tile1, tile2], simulate=True)
                self.matches = []

                # Revert swap
                self.tiles[i][j] = tile1
                self.tiles[i + 1][j] = tile2
                tile1.i = i
                tile2.i = i + 1

                if matches is not None:
                    return True

        return False
