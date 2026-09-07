from typing import TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.states.entity.BaseEntityState import BaseEntityState


_SHOT_DELAY = 0.15
_STATE_DURATION = 0.35


class PlayerBowState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

        # Drawing the bow equips it: idle/walk keep rendering it in hand
        # until a sword swing or a pot pickup clears this flag.
        self.entity.bow_equipped = True

        self.entity.offset_y = 5
        self.entity.offset_x = 0

        self.entity.change_animation(f"bow-{self.entity.direction}")

        # An arrow is fired once, after _SHOT_DELAY seconds in this state.
        self.arrow_fired = False
        self.elapsed = 0.0

    def _spawn_arrow(self) -> None:
        direction = self.entity.direction

        if direction == "left":
            x = self.entity.x - settings.TILE_SIZE
            y = self.entity.y + 2
        elif direction == "right":
            x = self.entity.x + self.entity.width
            y = self.entity.y + 2
        elif direction == "up":
            x = self.entity.x
            y = self.entity.y - settings.TILE_SIZE
        else:
            x = self.entity.x
            y = self.entity.y + self.entity.height

        projectile = self.entity.bow.fire(round(x), round(y), direction)
        self.dungeon.current_room.projectiles.append(projectile)

    def enter(self) -> None:
        settings.SOUNDS["bow"].stop()
        settings.SOUNDS["bow"].play()

        # Restart bow animation.
        self.entity.current_animation.reset()

    def update(self, dt: float) -> None:
        self.entity.interact_requested = False
        self.entity.sword_requested = False
        self.entity.shoot_bow_requested = False

        self.elapsed += dt

        if not self.arrow_fired and self.elapsed >= _SHOT_DELAY:
            self._spawn_arrow()
            self.arrow_fired = True

        if self.elapsed >= _STATE_DURATION:
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
