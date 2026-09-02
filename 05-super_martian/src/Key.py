from typing import Any

import pygame

from gale.camera import Camera
from gale.stencil import Stencil
from gale.timer import Timer

import settings
from src.GameItem import GameItem


class Key(GameItem):

    def __init__(self, block_x: float, block_y: float) -> None:
        super().__init__(
            x=block_x,
            # Start at the block's top edge so the key begins fully hidden
            y=block_y,
            width=16,
            height=16,
            texture_id="key",          
            frame_index=0,
            collidable=False,           
            consumable=True,
        )

        # The stencil clips away everything at or below this line.
        self.spawn_y: float = block_y

        # Destination y after the emergence tween completes
        target_y: float = block_y - 16

        Timer.tween(
            0.5,
            [(self, {"y": target_y})],
            ease_function_name="out_cubic",
            on_finish=self._on_emerged,
        )

    #is collidable when is merging? No. Wait for it
    def _on_emerged(self) -> None:
        self.collidable = True

    def render(self, surface: pygame.Surface, camera: Any) -> None:
        texture = settings.TEXTURES[self.texture_id]
        frame = settings.FRAMES[self.texture_id][self.frame_index]
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        image.blit(texture, (0, 0), frame)
       
        # sprite_rect in world coords
        sprite_rect = pygame.Rect(
            round(self.x), round(self.y), self.width, self.height
        )
        # Allowed visible region: any row strictly above the block top edge
        visible_region = pygame.Rect(
            round(self.x), 0, self.width, round(self.spawn_y)
        )
        # Intersection = the slice of the key that has emerged
        emerged = visible_region.clip(sprite_rect)

        # Convert to coordinates local to the image surface
        emerged.move_ip(-round(self.x), -round(self.y))

        stencil = Stencil((self.width, self.height))
        stencil.draw(lambda mask: mask.fill((255, 255, 255, 255), emerged))
        stencil.apply(image)

        dest = camera.apply(sprite_rect)
        surface.blit(image, dest)