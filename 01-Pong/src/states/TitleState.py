"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TitleState.
"""

import random

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.rendering import render_table


class TitleState(BaseState):
    def enter(self, pong) -> None:
        self.pong = pong

    def render(self, surface: pygame.Surface) -> None:
        render_table(surface, self.pong)

        render_text(
            surface,
            "PONG",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 5,
            settings.COLOR_GREEN,
            center=True,
        )

        render_text(
            surface,
            "SELECT MODE",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 3,
            settings.COLOR_WHITE,
            center=True,
        )

        options = [
            ("[1] PLAYER vs CPU", settings.COLOR_WHITE),
            ("[2] PLAYER 1 vs PLAYER 2", settings.COLOR_WHITE),
            ("[3] CPU vs CPU", settings.COLOR_WHITE),
            ("[4] Quit", settings.COLOR_WHITE),
        ]

        start_y = settings.VIRTUAL_HEIGHT / 2 - 18
        for index, (label, color) in enumerate(options):
            render_text(
                surface,
                label,
                settings.FONTS["large"],
                settings.VIRTUAL_WIDTH / 2,
                start_y + index * 26,
                color,
                center=True,
            )

        render_text(
            surface,
            "USE 1, 2 OR 3 TO START",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT - 30,
            settings.COLOR_GREEN,
            center=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "one" and input_data.pressed:
            self.pong.serving_player = random.randint(1, 2)
            self.state_machine.change("serve", pong=self.pong)
            self.pong.cpu1_active = True
            self.pong.cpu2_active = False
        elif input_id == "two" and input_data.pressed:
            self.pong.serving_player = random.randint(1, 2)
            self.state_machine.change("serve", pong=self.pong)
            self.pong.cpu1_active = False
            self.pong.cpu2_active = False
        elif input_id == "three" and input_data.pressed:
            self.pong.serving_player = random.randint(1, 2)
            self.state_machine.change("serve", pong=self.pong)
            self.pong.cpu1_active = True
            self.pong.cpu2_active = True
        elif input_id == "four" and input_data.pressed:
            self.quit()