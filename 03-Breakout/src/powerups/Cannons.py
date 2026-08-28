import random
from typing import TypeVar

from gale.factory import Factory

import settings
from src.Ball import Ball
from src.powerups.PowerUp import PowerUp

class Cannons(PowerUp):

    DURATION = 10.0

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 6)
        self.active_powerup = False
        self.render_square = True
        self.timer = 0.0

    def take(self, play_state: TypeVar("PlayState")) -> None:
        self.paddle = play_state.paddle
        self.render_square = False
        self.active = False
        self.active_powerup = True
        self.timer = 0.0
        play_state.cannons_powerup = self 

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        self.timer += dt

        if(self.timer >= Cannons.DURATION):
            self.active = False
            self.active_powerup = False
        

    def render(self, surface: pygame.Surface) -> None:
        
        if(self.render_square):
            surface.blit(
                settings.TEXTURES["spritesheet"],
                (self.x, self.y),
                settings.FRAMES["powerups"][self.frame],
            )

        if self.active_powerup:
            r = self.paddle.get_collision_rect()
            cannon_frame = settings.FRAMES["powerups"][10]
            surface.blit(settings.TEXTURES["spritesheet"], (r.left - 16, r.y), cannon_frame)
            surface.blit(settings.TEXTURES["spritesheet"], (r.right, r.y), cannon_frame)

