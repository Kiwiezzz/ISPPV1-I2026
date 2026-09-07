"""
This file contains BossInvertedState: the boss enters it when an arrow
hits it. For 5 seconds it renders with the inverted-colour sheet
(boss-inverted). During roughly the last 1.25 s it alternates quickly
between the inverted and the normal look, so the return to normal reads
as a fade rather than a hard cut, then it drops back to BossIdleState.

This 5 s window is also the boss's sword-vulnerability window in the
professor's spec; that part is wired up in a later step.
"""

from typing import TypeVar

import pygame

from src.states.entity.BaseEntityState import BaseEntityState

# Whole inverted window, seconds.
_DURATION = 5.0
# Trailing slice of the window during which the look flickers.
_FLICKER_WINDOW = 1.25
# How fast the flicker toggles, seconds per swap.
_FLICKER_INTERVAL = 0.1


class BossInvertedState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation("idle")
        self.elapsed = 0.0
        self.show_inverted = True
        self.entity.sword_vulnerable = True

    def exit(self) -> None:
        self.entity.sword_vulnerable = False

    def update(self, dt: float) -> None:
        # Freeze movement during vulnerability window.
        self.entity.held["move_left"] = False
        self.entity.held["move_right"] = False
        self.entity.held["move_up"] = False
        self.entity.held["move_down"] = False

        self.elapsed += dt

        if self.elapsed >= _DURATION:
            self.entity.change_state("idle")
            return

        remaining = _DURATION - self.elapsed

        if remaining <= _FLICKER_WINDOW:
            # Alternate on a fixed cadence regardless of frame rate.
            self.show_inverted = int(self.elapsed / _FLICKER_INTERVAL) % 2 == 0
        else:
            self.show_inverted = True

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        texture_id = "boss-inverted" if self.show_inverted else "boss"
        self.entity.render_sprite(surface, texture_id, anim.get_current_frame())
