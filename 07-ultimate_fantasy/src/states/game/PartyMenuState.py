from typing import Any

import pygame

from gale.state import BaseState

import settings
from src.gui.Menu import Menu

class PartyMenuState(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state
        self.menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 70,
            settings.VIRTUAL_HEIGHT / 2 - 48,
            140,
            96,
            items=[
                ("Party Status", self._show_party_status),
                ("Health Caracter", self._show_health_character),
                ("Health Team", self._show_health_team),
                ("Return to game", self.close),
            ],
            font=settings.FONTS["small"],
        )
  
        

    def close(self) -> None:
        self.state_machine.pop()

    def _show_party_status(self) -> None:
        from src.states.game.PartyStatus import PartyStatus

        self.state_machine.push(
            PartyStatus(self.state_machine), play_state=self.play_state
        )

    def _show_health_character(self) -> None:
        from src.states.game.HealthCaracter import HealthCaracter

        self.state_machine.push(
            HealthCaracter(self.state_machine), play_state=self.play_state
        )

    def _show_health_team(self) -> None:
        from src.states.game.HealthTeam import HealthTeam

        self.state_machine.push(
            HealthTeam(self.state_machine), play_state=self.play_state
        )

    # -- BaseState -------------------------------------------------------

    def update(self, dt: float) -> None:
        self.menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        self.menu.render(surface)

    