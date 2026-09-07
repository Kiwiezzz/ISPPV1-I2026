"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayerSwingSwordState.
"""

from typing import TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.states.entity.BaseEntityState import BaseEntityState


class PlayerSwingSwordState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

        # Swinging the sword puts the bow away.
        self.entity.bow_equipped = False

        # Render offset for spaced character sprite.
        self.entity.offset_y = 5
        self.entity.offset_x = 8

        # Hitbox based on where the player is and facing.
        direction = self.entity.direction

        if direction == "left":
            width, height = 8, 16
            x = self.entity.x - width
            y = self.entity.y + 2
        elif direction == "right":
            width, height = 8, 16
            x = self.entity.x + self.entity.width
            y = self.entity.y + 2
        elif direction == "up":
            width, height = 16, 8
            x = self.entity.x
            y = self.entity.y - height
        else:
            width, height = 16, 8
            x = self.entity.x
            y = self.entity.y + self.entity.height

        self.sword_hitbox = pygame.Rect(round(x), round(y), width, height)
        self.entity.change_animation(f"sword-{direction}")

        # Entities already damaged by this swing, so each swing lands once.
        self.already_hit = set()

    def enter(self) -> None:
        settings.SOUNDS["sword"].stop()
        settings.SOUNDS["sword"].play()

        # Restart sword swing animation.
        self.entity.current_animation.reset()

    def update(self, dt: float) -> None:
        self.entity.interact_requested = False

        if self.entity.sword_requested:
            self.entity.sword_requested = False
            self.entity.change_state("swing-sword")
            return

        for entity in self.dungeon.current_room.entities:
            if entity in self.already_hit or not entity.collides(self.sword_hitbox):
                continue

            # The boss shrugs off the sword unless it is in its vulnerable
            # state; every other entity is hit normally.
            if not getattr(entity, "sword_vulnerable", True):
                continue

            entity.damage(1)
            settings.SOUNDS["hit-enemy"].play()
            self.already_hit.add(entity)

        if self.entity.current_animation.times_played > 0:
            self.entity.current_animation.times_played = 0
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
