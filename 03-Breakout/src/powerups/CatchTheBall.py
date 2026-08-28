import random
from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp


class CatchTheBall(PowerUp):

    DURATION = 8.0

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 7)
        self.timer = 0.0
        self.active_powerup = False

    def take(self, play_state: TypeVar("PlayState")) -> None:
        self.active = False
        self.active_powerup = True
        self.timer = 0.0
        play_state.catch_powerup = self

    def update(self, dt: float) -> None:
        self.timer += dt
        self.y += self.vy * dt
        if self.timer >= CatchTheBall.DURATION:
            self.active_powerup = False
