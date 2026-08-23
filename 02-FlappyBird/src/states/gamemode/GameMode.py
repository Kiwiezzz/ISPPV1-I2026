from abc import ABC, abstractmethod
import pygame

from gale.input_handler import InputData

from src.Bird import Bird
from src.World import World

class GameMode(ABC):
    @abstractmethod
    def update(self, dt: float, bird: Bird, world: World) -> None:
        pass

    @abstractmethod
    def is_game_over(self, bird: Bird, world: World) -> bool:
        pass

    @abstractmethod
    def reset(self, generate_logs: bool) -> None:
        pass

    @abstractmethod
    def on_score(self, bird: Bird, world: World) -> None:
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface, score: int) -> None:
        pass

    @abstractmethod
    def on_input(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        pass