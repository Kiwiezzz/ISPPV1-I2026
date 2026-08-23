import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World

class PauseState(BaseState):
    def enter(self, **params: dict) -> None:

        self.world = params["world"]
        self.bird = params["bird"]
        self.score = params["score"]
        self.game_mode = params["game_mode"]


        self.options = [
                    "Continue",
                    "Restart",
                    "Exit",
                ]
        
        self.selected_option = 0

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
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        
        render_text(
            surface,
            "Paused",
            settings.FONTS["huge"],
            settings.VIRTUAL_WIDTH / 2,
            100,
            settings.COLOR_WHITE,
            center=True,
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

        if input_id == "pause":
            self.state_machine.change("playing", world=self.world, bird=self.bird, score=self.score, game_mode=self.game_mode)
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
                self.state_machine.change("playing", world=self.world, bird=self.bird, score=self.score, game_mode=self.game_mode)
            elif(self.selected_option == 1):
                self.state_machine.change("count_down", game_mode=self.game_mode)
            elif(self.selected_option == 2):
                self.state_machine.change("title")
