import pygame
import settings
from src.Tile import Tile

class LineBomb(Tile):
    def __init__(self, i: int, j: int, color: int, variety: int = 0) -> None:
        # force variety=0 so the base tile is always flat.
        super().__init__(i, j, color, variety=0)
        self.is_line_bomb = True

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        # Draw the base flat tile
        super().render(surface, offset_x, offset_y)
        
        # Draw the +4 overlay image
        settings.TEXTURES["line-bomb"].set_alpha(128)
        surface.blit(
            settings.TEXTURES["line-bomb"],
            (self.x + offset_x, self.y + offset_y)
        )

    def get_explosion_targets(self, board) -> list:
        targets = []
        # Get all the tiles in the same row
        for j in range(len(board.tiles[0])):
            if board.tiles[self.i][j] is not None:
                targets.append(board.tiles[self.i][j])
        
        # Get all the tiles in the same column
        for i in range(len(board.tiles)):
            if board.tiles[i][self.j] is not None:
                if board.tiles[i][self.j] not in targets:
                    targets.append(board.tiles[i][self.j])
                    
        return targets
