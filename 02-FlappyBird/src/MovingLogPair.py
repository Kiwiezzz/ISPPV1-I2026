import math

import settings
from src.LogPair import LogPair


class MovingLogPair(LogPair):
    def __init__(self, x: float, y: float, gap: float = None) -> None:
        super().__init__(x, y, gap)
        self.base_gap = self.gap
        self.timer = 0.0
        self.closed = False

    def update(self, dt: float) -> None:
        super().update(dt)

        self.timer += dt
        # The sin() function is for oscillating motion
        self.gap = (self.base_gap / 2) + math.sin(self.timer * 3) * (self.base_gap / 2)

        #Tolerance margin
        if self.gap <= 2:
            if not self.closed:
                settings.SOUNDS["collision_log"].play()
                self.closed = True
        else:
            self.closed = False
