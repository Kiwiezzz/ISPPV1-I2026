"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Variables for Drag & Drop. Store Original Values of dragged Tile if the movement fail
        self.dragged_tile = None
        self.dragged_start_i = -1
        self.dragged_start_j = -1
        self.dragged_start_x = -1
        self.dragged_start_y = -1

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = int(self.level * 1.25 * 1000 * 1.5)

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

        if self.active and self.dragged_tile is not None:
            #Get the raw position of the Mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            #And then scale that raw position to virtual of the game            
            mouse_x = mouse_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            mouse_y = mouse_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            
            self.dragged_tile.x = mouse_x - self.board.x - settings.TILE_SIZE // 2
            self.dragged_tile.y = mouse_y - self.board.y - settings.TILE_SIZE // 2

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        #Draw the dragged Tile
        if self.dragged_tile is not None:
            self.dragged_tile.render(surface, self.board.x, self.board.y)

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click":
            if input_data.pressed:
                if self.dragged_tile is None:
                    pos_x, pos_y = input_data.position
                    pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                    pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                    i = (pos_y - self.board.y) // settings.TILE_SIZE
                    j = (pos_x - self.board.x) // settings.TILE_SIZE
                    
                    if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                        self.dragged_tile = self.board.tiles[i][j]
                        self.dragged_start_i = i
                        self.dragged_start_j = j
                        self.dragged_start_x = self.dragged_tile.x
                        self.dragged_start_y = self.dragged_tile.y

            elif input_data.released:
                if self.dragged_tile is not None:
                    pos_x, pos_y = input_data.position
                    pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                    pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                    
                    end_i = (pos_y - self.board.y) // settings.TILE_SIZE
                    end_j = (pos_x - self.board.x) // settings.TILE_SIZE
                    
                    # Check if end position is valid and adjacent to start position
                    if end_i == self.dragged_start_i and end_j == self.dragged_start_j:
                        # If the tile is a bomb, explode it
                        tile = self.dragged_tile
                        if getattr(tile, 'is_line_bomb', False) or getattr(tile, 'is_color_bomb', False):
                            self.active = False
                            self.board.matches.append([tile])
                            
                            destroyed_tiles = self.board.remove_matches()
                            self.score += len(destroyed_tiles) * 50
                            
                            falling_tiles = self.board.get_falling_tiles()
                            Timer.tween(
                                0.25,
                                falling_tiles,
                                on_finish=lambda: self._calculate_matches(
                                    [item[0] for item in falling_tiles]
                                ),
                            )
                            settings.SOUNDS["bomb"].stop()
                            settings.SOUNDS["bomb"].play()
                        
                        else:
                            # return to original position if not a bomb
                            self.dragged_tile.x = self.dragged_start_x
                            self.dragged_tile.y = self.dragged_start_y
                        
                        self.dragged_tile = None
                        
                    elif (0 <= end_i < settings.BOARD_HEIGHT and 0 <= end_j < settings.BOARD_WIDTH and
                        (abs(end_i - self.dragged_start_i) + abs(end_j - self.dragged_start_j) == 1)):
                        
                        target_tile = self.board.tiles[end_i][end_j]
                        
                        # Temporarily swap in the board
                        self.board.tiles[self.dragged_start_i][self.dragged_start_j] = target_tile
                        self.board.tiles[end_i][end_j] = self.dragged_tile
                        
                        self.dragged_tile.i = end_i
                        self.dragged_tile.j = end_j
                        target_tile.i = self.dragged_start_i
                        target_tile.j = self.dragged_start_j
                        
                        # Check matches
                        matches = self.board.calculate_matches_for([self.dragged_tile, target_tile], simulate=True)
                        
                        if matches is None:
                            # Revert swap (invalid move)
                            self.board.tiles[self.dragged_start_i][self.dragged_start_j] = self.dragged_tile
                            self.board.tiles[end_i][end_j] = target_tile
                            
                            self.dragged_tile.i = self.dragged_start_i
                            self.dragged_tile.j = self.dragged_start_j
                            target_tile.i = end_i
                            target_tile.j = end_j
                            
                            # Animate dragged tile back to its original spot
                            self.active = False
                            Timer.tween(
                                0.25,
                                [
                                    (self.dragged_tile, {"x": self.dragged_start_x, "y": self.dragged_start_y}),
                                ],
                                on_finish=lambda: setattr(self, 'active', True)
                            )
                        else:
                            # Valid swap
                            self.active = False
                            
                            target_target_x = self.dragged_start_j * settings.TILE_SIZE
                            target_target_y = self.dragged_start_i * settings.TILE_SIZE
                            
                            dragged_target_x = end_j * settings.TILE_SIZE
                            dragged_target_y = end_i * settings.TILE_SIZE
                            
                            # Use variables in local scope for the lambda
                            dtile = self.dragged_tile
                            ttile = target_tile
                            Timer.tween(
                                0.25,
                                [
                                    (dtile, {"x": dragged_target_x, "y": dragged_target_y}),
                                    (ttile, {"x": target_target_x, "y": target_target_y}),
                                ],
                                on_finish=lambda: self._calculate_matches([dtile, ttile])
                            )
                    else:
                        # Dropped on invalid cell or not adjacent cell
                        self.active = False
                        Timer.tween(
                            0.25,
                            [
                                (self.dragged_tile, {"x": self.dragged_start_x, "y": self.dragged_start_y}),
                            ],
                            on_finish=lambda: setattr(self, 'active', True)
                        )
                        
                    self.dragged_tile = None

    def _calculate_matches(self, tiles: List) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            # The board is stable. Check if there are any valid moves left.
            # If not, recreate the board until at least one valid move exists.
            while not self.board.has_possible_matches():
                self.board._initialize_tiles()
                
            self.active = True
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        initial_match_count = sum(len(match) for match in matches)
        for match in matches:
            self.score += len(match) * 50

        destroyed_tiles = self.board.remove_matches()
        
        # Extra points for chain reactions from bombs
        extra_destroyed = max(0, len(destroyed_tiles) - initial_match_count)
        self.score += extra_destroyed * 50

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )
