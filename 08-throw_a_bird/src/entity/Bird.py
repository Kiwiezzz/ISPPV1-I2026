"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Bird: the parrot sitting in the slingshot,
ported from main.script + the parrot.go. It is a plain dynamic circle
body -- heavy, invulnerable (no destructible.script attached, matching
the original) -- driven entirely by PlayState (aiming/panning/flinging
live there, since in the original they are main.script's own concerns,
not the parrot's).
"""

import math

import pygame

from gale.physics.shapes import CircleShape
from gale.physics.world import World

import settings
from src.definitions.entity import BIRDS, density_for_circle


class Bird:
    def __init__(self, world: World, x: float, y: float, color: str = "red") -> None:
        stats = BIRDS[color]
        self.color: str = color
        self.radius: float = stats["radius"]
        self.mass: float = stats["mass"]

        density = density_for_circle(self.mass, self.radius)
        self.body = world.create_dynamic_body(
            x,
            y,
            CircleShape(
                radius=self.radius,
                density=density,
                friction=stats["friction"],
                restitution=stats["restitution"],
            ),
        )
        self.body.set_damping(stats["linear_damping"], stats["angular_damping"])
        self.body.user_data = self

        self.initial_position = pygame.Vector2(x, y)
        self._normal_image = settings.TEXTURES[stats["sprite"]]
        self._damaged_image = settings.TEXTURES[stats["damaged_sprite"]]

        # Set once this bird touches anything solid -- ground or another
        # body -- and never cleared until the next reset(). This is what
        # the split ability (spec 1) checks before letting a throw split:
        # once a bird has hit something, splitting is off for that throw.
        self.has_collided: bool = False

        # Set once this bird has used its split (only the blue bird ever
        # can). Distinct from has_collided: a bird can only split once
        # per throw even if it never collides again, so pressing split
        # twice in a row mid-air must not split it a second time.
        self.powerup_activated: bool = False

    @property
    def position(self) -> pygame.Vector2:
        return self.body.position

    def fixed_update(self) -> None:
        if self.has_collided:
            return

        for other in self.body.touching_bodies:
            # Wind zones are sensors, not something the bird actually hit
            # (see Level._build_wind_zones) -- touching_bodies reports
            # sensor overlaps too, so they need to be skipped explicitly.
            if other.user_data == "wind":
                continue

            self.has_collided = True
            break

    def reset(self) -> None:
        """
        Put the bird back to rest in the slingshot, ready for another
        throw -- ported from main.script's idle_frames > 100 branch.
        """
        self.body.position = self.initial_position
        self.body.angle = 0.0
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0.0
        self.has_collided = False
        self.powerup_activated = False

    def render(self, surface: pygame.Surface, camera) -> None:
        image = self._damaged_image if self.has_collided else self._normal_image
        diameter = max(1, round(self.radius * 2 * camera.zoom))
        scaled = pygame.transform.smoothscale(image, (diameter, diameter))
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.body.angle))
        rect = rotated.get_rect(center=camera.world_to_screen(self.body.position))
        surface.blit(rotated, rect)
