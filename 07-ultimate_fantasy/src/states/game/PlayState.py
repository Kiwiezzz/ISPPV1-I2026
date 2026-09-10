"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState: hosts the World (overworld
regions + party) for as long as the player is out of battle.
"""

from typing import Any, Dict, Optional

import pygame

from gale.save import SaveManager
from gale.state import BaseState

import settings
from src.definitions.entity import ENTITY_DEFS
from src.world.World import World

# Human-friendly labels for World.current_region_name, shown on a save
# slot's stat card (see SlotSelectState) instead of the raw internal key.
REGION_LABELS = {
    "center": "Town",
    "north": "North",
    "south": "South",
    "east": "East",
    "west": "West",
}


class PlayState(BaseState):
    def enter(
        self,
        party_genders: Dict[int, str],
        save_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.world = World(self.state_machine, party_genders)

        if save_data is not None:
            self.world.load_dict(save_data)

    def save_game(self, slot: str) -> None:
        """Saves to `slot`, tagging it with the display stats a save-select
        screen needs (see SlotSelectState) as SaveManager metadata -- read
        back later via SaveManager.read_metadata, without loading (or
        migrating) the full save data."""
        party = self.world.party
        names = [
            ENTITY_DEFS["characters"][k][party.party_genders[k]]["name"]
            for k in sorted(party.characters.keys())
            if not party.characters[k].dead
        ]
        levels = [character.level for character in party.characters.values()]
        avg_level = round(sum(levels) / len(levels), 1) if levels else 1

        SaveManager().save(
            slot,
            self.world.to_dict(),
            party_names=names,
            party_level=avg_level,
            region_label=REGION_LABELS.get(
                self.world.current_region_name, self.world.current_region_name
            ),
        )
        self.world.dirty = False

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id == "pause" and input_data.pressed:
            from src.states.game.PauseMenuState import PauseMenuState

            self.world.freeze_party()
            self.state_machine.push(PauseMenuState(self.state_machine), play_state=self)
            return

        self.world.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
