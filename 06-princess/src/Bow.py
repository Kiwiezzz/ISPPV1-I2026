from gale.factory import Factory

from src.Arrow import Arrow
from src.Projectile import Projectile


class Bow:
    def __init__(self) -> None:
        self.arrow_factory = Factory(Arrow)

    def fire(self, x: float, y: float, direction: str) -> Projectile:
        arrow = self.arrow_factory.create(x, y, {"direction": direction})
        return Projectile(arrow, direction)
