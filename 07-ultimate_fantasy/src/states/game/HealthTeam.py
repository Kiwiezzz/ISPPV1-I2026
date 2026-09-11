from typing import Any

import pygame

from gale.state import BaseState

import settings
from src.states.game.ShowTextState import ShowTextState


class HealthTeam(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state
        party = play_state.world.party
        healer, action = self._heal_action(party)

        if healer is None:
            text = "No one can heal the whole team right now"
        else:
            alive = [c for c in party.characters.values() if not c.dead]
            action["func"](healer, alive, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()
            play_state.world.dirty = True
            text = "Team has been healed"

        self.state_machine.push(
            ShowTextState(self.state_machine),
            color=(255, 255, 255),
            text=text,
            on_complete=self.close,
        )

    def _heal_action(self, party: Any):
        for character in party.characters.values():
            if character.dead:
                continue
            for action in character.actions:
                if action["target_type"] == "character" and not action["require_target"]:
                    return character, action
        return None, None

    def close(self) -> None:
        self.state_machine.pop()

    def update(self, dt: float) -> None:
        pass

    def on_input(self, input_id: str, input_data: Any) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass
