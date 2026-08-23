"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PlayingState.
"""

from typing import Optional

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World
from src.states.gamemode.GameMode import GameMode


class PlayingState(BaseState):
    def enter(self, game_mode: GameMode, world: Optional[World] = None, bird: Optional[Bird] = None, score: Optional[int] = 0) -> None:
        self.game_mode = game_mode
        self.world = world if world is not None else World()
        self.game_mode.reset(True)
        self.bird = bird if bird is not None else Bird(
            settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
            settings.BIRD_WIDTH,
            settings.BIRD_HEIGHT,
        )
        self.score = score

    def update(self, dt: float) -> None:
        self.game_mode.update(dt, self.bird, self.world)

        if self.game_mode.is_game_over(self.bird, self.world):
            settings.SOUNDS["explosion"].play()
            settings.SOUNDS["hurt"].play()
            self.state_machine.change("count_down", game_mode=self.game_mode)
            return

        if self.game_mode.on_score(self.bird, self.world):
            self.score += 1
            settings.SOUNDS["score"].play()

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )


    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.change("pause", world=self.world, bird=self.bird, score=self.score, game_mode=self.game_mode)
        else:
            self.game_mode.on_input(input_id, input_data, self.bird)
