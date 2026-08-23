import pygame
import random

from gale.input_handler import InputData
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World
from src.states.gamemode.GameMode import GameMode
from src.LogPair import LogPair
from gale.factory import Factory


class NormalMode(GameMode):

    def __init__(self, generate_logs: bool = False) -> None:
        self.generate_logs: bool = generate_logs
        self.logs_spawn_timer = 0.0
        self.last_log_y = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        self.log_pair_factory: Factory = Factory(LogPair)

    def reset(self, generate_logs: bool) -> None:
        self.generate_logs = generate_logs
        


    def update(self, dt: float, bird: Bird, world: World) -> None:

        #Bool que genera los troncos
        if self.generate_logs:
            self.logs_spawn_timer += dt

            if self.logs_spawn_timer >= settings.TIME_TO_SPAWN_LOGS:
                self.logs_spawn_timer = 0.0
                y = max(
                    -settings.LOG_HEIGHT + 10,
                    min(
                        self.last_log_y + random.randint(-20, 20),
                        settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT,
                    ),
                )
                self.last_log_y = y
                world.add_log(self.log_pair_factory.create(settings.VIRTUAL_WIDTH, y))
        #-----------------------------------------------------------------------------------------

        bird.update(dt)
        world.update(dt)

    def is_game_over(self, bird: Bird, world: World) -> bool:
        return world.collides(bird.get_rect())

    def on_score(self, bird: Bird, world: World) -> bool:
        return world.update_scored(bird.get_rect())

    def render(self, surface: pygame.Surface, score: int) -> None:
        render_text(
            surface,
            f"Score: {score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()
