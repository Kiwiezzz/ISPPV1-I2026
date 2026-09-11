from typing import Any, Optional, Tuple

import pygame

from gale.state import BaseState

import settings
from src.gui.Menu import Menu
from src.states.game.ShowTextState import ShowTextState


class HealthCaracter(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state
        self.party = play_state.world.party
        self.healer, self.action = self._heal_action()
        self.menu: Optional[Menu] = None

        if self.healer is None:
            self.state_machine.push(
                ShowTextState(self.state_machine),
                color=(255, 255, 255),
                text="No one can heal an ally right now",
                on_complete=self.close,
            )
            return

        items = [
            (character.name, self._make_selector(character))
            for character in self.party.characters.values()
            if not character.dead
        ]
        items.append(("Cancel", self.close))

        self.menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 70,
            settings.VIRTUAL_HEIGHT / 2 - 48,
            140,
            96,
            items=items,
            font=settings.FONTS["small"],
        )

    def _heal_action(self) -> Tuple[Optional[Any], Optional[dict]]:
        for character in self.party.characters.values():
            if character.dead:
                continue
            for action in character.actions:
                if action["target_type"] == "character" and action["require_target"]:
                    return character, action
        return None, None

    def _make_selector(self, target: Any):
        return lambda: self._heal(target)

    def _heal(self, target: Any) -> None:
        amount = self.action["func"](self.healer, target, self.action.get("strength"))
        settings.SOUNDS[self.action["sound_effect"]].play()
        self.play_state.world.dirty = True

        self.state_machine.push(
            ShowTextState(self.state_machine),
            color=(255, 255, 255),
            text=f"{target.name} recovered {amount} HP",
            on_complete=self.close,
        )

    def close(self) -> None:
        self.state_machine.pop()

    def update(self, dt: float) -> None:
        if self.menu is not None:
            self.menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if self.menu is None or not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        if self.menu is not None:
            self.menu.render(surface)
