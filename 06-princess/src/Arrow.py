from src.GameObject import GameObject
from src.definitions.game_objects import GAME_OBJECT_DEFS


class Arrow(GameObject):
    def __init__(self, x: float, y: float, direction: str) -> None:
        super().__init__(GAME_OBJECT_DEFS["arrow"], x, y)
        self.state = direction
