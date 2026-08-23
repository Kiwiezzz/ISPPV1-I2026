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


class HardMode(GameMode):

    def __init__(self, generate_logs: bool = False) -> None:
        self.generate_logs: bool = generate_logs
        self.logs_spawn_timer = 0.0
        self.last_log_y = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        self.current_spawn_interval = random.uniform(1.2, 2.5)
        self.log_pair_factory: Factory = Factory(LogPair)

    def reset(self, generate_logs: bool) -> None:
        self.generate_logs = generate_logs
        self.logs_spawn_timer = 0.0
        self.current_spawn_interval = random.uniform(1.2, 2.5)
        self.last_log_y = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        


    def update(self, dt: float, bird: Bird, world: World) -> None:

        if self.generate_logs:
            self.logs_spawn_timer += dt

            if self.logs_spawn_timer >= self.current_spawn_interval:
                self.logs_spawn_timer = 0.0

                max_y_change = int((self.current_spawn_interval - 1.0) * 80) 
                
                y = max(
                    -settings.LOG_HEIGHT + 10,
                    min(
                        self.last_log_y + random.randint(-max_y_change, max_y_change),
                        settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT,
                    ),
                )
                self.last_log_y = y
                

                gap = random.randint(60, 80)
               
                world.add_log(LogPair(settings.VIRTUAL_WIDTH, y, gap=gap))
                
                self.current_spawn_interval = random.uniform(1.2, 2.5)

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
        elif input_id == "a":
            if input_data.pressed:
                bird.vx = -settings.BIRD_SPEED
            elif bird.vx < 0:
                bird.vx = 0
        elif input_id == "d":
            if input_data.pressed:
                bird.vx = settings.BIRD_SPEED
            elif bird.vx > 0:
                bird.vx = 0
