"""
This file contains the class Fireball: the slow projectile the boss
shoots. It is aimed once -- at the point the player occupied the moment
it was created -- and then travels that straight line until it leaves the
room. It does not home in on the player.
"""

import math
from typing import Any

import pygame

from gale.animation import Animation

import settings

# Slow on purpose: just above the player's walk speed (60) so it is
# threatening but always dodgeable.
_SPEED = 70
_SIZE = 16
# The visible flame is smaller than its 16x16 cell; shrink the hitbox so
# near misses read as misses.
_HITBOX_INSET = 3


class Fireball:
    def __init__(
        self, x: float, y: float, target_x: float, target_y: float
    ) -> None:
        # (x, y) and (target_x, target_y) are centre points.
        self.width = _SIZE
        self.height = _SIZE
        self.x = x - _SIZE / 2
        self.y = y - _SIZE / 2

        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)

        if distance == 0:
            dx, dy, distance = 0.0, 1.0, 1.0

        self.vel_x = _SPEED * dx / distance
        self.vel_y = _SPEED * dy / distance

        # Snap the aim to the nearest cardinal just for the sprite.
        if abs(self.vel_x) >= abs(self.vel_y):
            self.direction = "right" if self.vel_x >= 0 else "left"
        else:
            self.direction = "down" if self.vel_y >= 0 else "up"

        self.animation = Animation([1, 2, 3, 4, 5, 6], 0.08)

        self.dead = False

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x + _HITBOX_INSET),
            round(self.y + _HITBOX_INSET),
            self.width - 2 * _HITBOX_INSET,
            self.height - 2 * _HITBOX_INSET,
        )

    def collides(self, target: Any) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())

    def update(self, dt: float) -> None:
        if self.dead:
            return

        self.animation.update(dt)

        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        left = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
        right = settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2
        top = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE
        bottom = (
            settings.MAP_HEIGHT * settings.TILE_SIZE
            + settings.MAP_RENDER_OFFSET_Y
            - settings.TILE_SIZE
        )

        if (
            self.x + self.width <= left
            or self.x >= right
            or self.y + self.height <= top
            or self.y >= bottom
        ):
            self.dead = True

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        texture_id = f"fireball-{self.direction}"
        surface.blit(
            settings.TEXTURES[texture_id],
            (round(self.x + offset_x), round(self.y + offset_y)),
            settings.frame(texture_id, self.animation.get_current_frame()),
        )
