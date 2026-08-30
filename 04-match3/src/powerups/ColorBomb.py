import pygame
import settings
from src.Tile import Tile

class ColorBomb(Tile):
    def __init__(self, i: int, j: int, color: int, variety: int = 0) -> None:
        super().__init__(i, j, color, 0)
        self.is_color_bomb = True

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:

        super().render(surface, offset_x, offset_y)
           
        # Draw the +5 overlay image
        settings.TEXTURES["color-bomb"].set_alpha(128)
        surface.blit(
            settings.TEXTURES["color-bomb"],
            (self.x + offset_x, self.y + offset_y)
        )

    # Return all the tiles of the same color of the bomb
    def get_explosion_targets(self, board) -> list:
        targets = []
        for row in board.tiles:
            for tile in row:
                if tile is not None and tile.color == self.color:
                    targets.append(tile)
        return targets
