"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class TitleScreenState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World
from src.states.gamemode.NormalMode import NormalMode
from src.states.gamemode.HardMode import HardMode


class TitleScreenState(BaseState):
    def enter(self) -> None:
        pygame.mixer.music.play(loops=-1)
        self.world = World()
        self.options = [
                    "Normal Mode",
                    "Hard Mode",
                    "Exit",
                ]
        
        self.selected_option = 0

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        render_text(
            surface,
            "Flappy Bird",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 3,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
        for index, option in enumerate(self.options):
            color = (255, 255, 0) if index == self.selected_option else settings.COLOR_WHITE
        
            render_text(
                surface,
                option,
                settings.FONTS["medium"],
                settings.VIRTUAL_WIDTH / 2,
                180 + index * 40,
                color,
                center=True,
            )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return
        
        if input_id == "w" or input_id == "up":
            self.selected_option -= 1

            if self.selected_option < 0:
                self.selected_option = len(self.options) - 1

        elif input_id == "s" or input_id == "down":
            self.selected_option += 1

            if self.selected_option >= len(self.options):
                self.selected_option = 0

        elif input_id == "confirm" and input_data.pressed:
            if(self.selected_option == 0):
                self.state_machine.change("count_down", game_mode=NormalMode())
            elif(self.selected_option == 1):
                self.state_machine.change("count_down", game_mode=HardMode())
            elif(self.selected_option == 2):
                self.quit()
