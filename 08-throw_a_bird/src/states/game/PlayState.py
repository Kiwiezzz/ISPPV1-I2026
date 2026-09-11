"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState, ported from main.script: the
whole per-frame update/input loop -- aiming, panning, flinging the bird,
camera follow-and-zoom, and idle-detection to reset the bird back to the
slingshot once a shot has settled.

Deviation from the Lua source: main.script disables the parrot's
collisionobject at rest and re-enables it only once flung, so gravity
and everything else leaves it alone until it is thrown.
gale.physics.Body has no enable/disable toggle for an existing fixture,
so instead the bird is held in place by brute force every frame it is
neither being aimed nor already in flight (_hold_bird_at_rest): its
position/velocity are pinned back to the slingshot each update(), which
cancels out whatever one frame of gravity would have done. The bird
remains a normal dynamic body throughout (nothing in the level ever
reaches the slingshot's position anyway), it is just re-pinned faster
than it can visibly fall.
"""

import math
import random
from typing import List

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.physics.world import World
from gale.state import BaseState
from gale.text import render_text

import settings
from src.entity.Bird import Bird
from src.world.Level import Level

# How close (world pixels) a press has to land to the bird to start
# aiming instead of panning the camera.
AIM_GRAB_RADIUS = 50

# The pull-back vector is clamped to this length (world pixels) both
# while aiming (how far the bird can be dragged back) and when computing
# the launch impulse on release.
MAX_PULL_DISTANCE = 150

# Scales the (clamped) pull-back vector into a launch impulse. Not a
# port of the original's `950` (a force applied for a single Defold
# physics step, at Defold's own physics.scale) -- chosen instead, by
# testing actual throws, so a full pull-back (MAX_PULL_DISTANCE) launches
# the bird fast enough to comfortably clear the gap and reach the tower
# under gale's default gravity, factoring in the energy the bird's own
# high friction/low restitution shed on its first bounce.
#
# This is the only tuning number that matters here, regardless of the
# bird's mass: gale.physics.Body.apply_impulse(ix, iy) divides by
# pixels_per_meter before hand it to Box2D, and Box2D's resulting
# delta-v is impulse / mass -- so passing an impulse of
# `pull * FLING_IMPULSE_SCALE * mass` (mirroring the Lua source's own
# `direction * 950 * parrot_mass`, force proportional to mass) makes
# mass cancel out of the result: launch speed is just
# `pull * FLING_IMPULSE_SCALE`.
#
# 10.5 (barely cleared the gap) was bumped to 16.0 (comfortably punched
# into the tower) per feedback that throws felt too weak -- then walked
# back to the average of the two, 13.25, per feedback that 16.0 then felt
# too strong.
FLING_IMPULSE_SCALE = 13.25

# Spec 1: each fresh bird loaded onto the slingshot has this chance of
# being the blue (split) bird instead of the plain red one.
BLUE_BIRD_CHANCE = 0.5

# How far off the original heading (degrees) the two side birds fly once
# a blue bird splits -- one rotated + this, the other - this, around
# whatever velocity the original bird had at the moment of the split.
SPLIT_ANGLE_DEGREES = 20.0

# How far the two side birds spawn from the center bird, along their own
# heading, as a multiple of their own radius. Needed because
# touching_bodies treats any overlap as a collision (see
# Bird.fixed_update): birds created on the same point would start
# overlapped and immediately register as already hit.
SPLIT_SPAWN_OFFSET_RADII = 3.0

# A shot is considered "settled" once the bird's linear/angular velocity
# has been below these thresholds for IDLE_FRAMES_LIMIT consecutive
# frames (~1.6s at 60fps) -- ported from main.script, retuned for gale's
# pixel/physics scale (angular velocity here is radians/second, not
# Defold's units).
IDLE_LINEAR_SPEED_THRESHOLD = 30
IDLE_ANGULAR_SPEED_THRESHOLD = 0.3
IDLE_FRAMES_LIMIT = 100

CAMERA_FOLLOW_RATE = 6.0
CAMERA_ZOOM_LERP_RATE = 3.0
CAMERA_ZOOM_MIN = 1.0
CAMERA_ZOOM_MAX = 1.5
CAMERA_PAN_MARGIN = 300

HUD_TEXT = "Drag the bird to aim and release to fling. Drag elsewhere to pan."


class PlayState(BaseState):
    def enter(self) -> None:
        self.world = World(gravity=settings.GRAVITY)

        self.level = Level(self.world)
        # self.bird is the one aimed, flung, and used as the zoom/camera
        # reference; self.birds is every bird currently alive (still
        # just [self.bird] until a split adds two more).
        self.birds: List[Bird] = []
        self._spawn_bird()

        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.camera.x, self.camera.y = self.bird.position
        self.camera_target = pygame.Vector2(self.camera.x, self.camera.y)
        self.camera.follow(self.camera_target, rate=CAMERA_FOLLOW_RATE)
        # Mirrors main.script's self.camera_zoom (ranges 1..1.5, bigger
        # means "farther away"); gale's own Camera.zoom is the inverse
        # (bigger means "closer"), so it is always set to 1/this ratio.
        self.camera_zoom_ratio = 1.0
        self.camera.zoom = 1.0

        self.aiming = False
        self.panning = False
        self.flinging = False
        self.idle_frames = 0

        self.pressed_position = pygame.Vector2()
        self.pressed_camera_target = pygame.Vector2()
        self.aim_offset = pygame.Vector2()

    def fixed_update(self) -> None:
        # Driven by gale.game.Game's own accumulator (added in gale
        # 1.10.0) instead of calling self.world.update(dt) here, which
        # would otherwise run a second, redundant accumulator on top of
        # World's own.
        self.world.fixed_update()
        self.level.fixed_update()

        for bird in self.birds:
            bird.fixed_update()

    def update(self, dt: float) -> None:
        self.level.update(dt)

        if self.level.all_enemies_defeated:
            self.state_machine.change("victory")
            return

        if self.flinging:
            self.camera_target.update(self._birds_centroid())
            self._update_idle()
        elif self.aiming:
            self._hold_bird_while_aiming()
        else:
            self._hold_bird_at_rest()

        self._update_zoom(dt)
        self.camera.update(dt)

    def _spawn_bird(self) -> None:
        """Loads a fresh bird for a new throw, rolling its color (see
        BLUE_BIRD_CHANCE). Built from scratch rather than repositioning
        the old one, since red/blue differ in radius/mass, which has to
        be set when the physics body is created. Destroys every bird
        still in self.birds first, not just self.bird, since a split
        throw can leave three of them scattered around the level."""
        for bird in self.birds:
            self.world.destroy_body(bird.body)

        color = "blue" if random.random() < BLUE_BIRD_CHANCE else "red"
        self.bird = Bird(
            self.world, self.level.bird_start.x, self.level.bird_start.y, color=color
        )
        self.birds = [self.bird]

    def _hold_bird_at_rest(self) -> None:
        self.bird.reset()

    def _hold_bird_while_aiming(self) -> None:
        # world.update(dt) above still steps gravity on the bird every
        # frame regardless of aiming state (gale.physics.Body has no
        # enable/disable toggle -- see the module docstring), and
        # _on_touch_motion only fires on mouse-motion *events*, not every
        # frame. Without re-pinning here too, any frame with no fresh
        # motion event lets gravity accumulate velocity that then snaps
        # the bird around erratically the moment position gets set again.
        # Re-applying the held offset and zeroing velocity every frame
        # keeps the bird glued to the mouse the whole time it is aiming.
        self.bird.body.position = self.bird.initial_position - self.aim_offset
        self.bird.body.velocity = (0, 0)
        self.bird.body.angular_velocity = 0.0

    def _birds_centroid(self) -> pygame.Vector2:
        total = pygame.Vector2()
        for bird in self.birds:
            total += bird.position
        return total / len(self.birds)

    def _update_idle(self) -> None:
        # A split throw only settles once every bird in self.birds has
        # slowed down, not just self.bird.
        all_settled = all(
            bird.body.velocity.length() < IDLE_LINEAR_SPEED_THRESHOLD
            and abs(bird.body.angular_velocity) < IDLE_ANGULAR_SPEED_THRESHOLD
            for bird in self.birds
        )

        if all_settled:
            self.idle_frames += 1

            if self.idle_frames > IDLE_FRAMES_LIMIT:
                self.flinging = False
                self.idle_frames = 0
                self._spawn_bird()
                self.camera_target.update(self.bird.position)
        else:
            self.idle_frames = 0

    def _update_zoom(self, dt: float) -> None:
        distance = abs(self._birds_centroid().x - self.bird.initial_position.x)
        reach = max(1.0, self.bird.initial_position.x)
        target_ratio = max(
            CAMERA_ZOOM_MIN, min(CAMERA_ZOOM_MAX, math.sqrt(distance / reach))
        )
        factor = 1.0 - math.exp(-CAMERA_ZOOM_LERP_RATE * dt)
        self.camera_zoom_ratio += (target_ratio - self.camera_zoom_ratio) * factor
        self.camera.zoom = 1.0 / self.camera_zoom_ratio

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BG_COLOR)
        self.level.render(surface, self.camera)

        for bird in self.birds:
            bird.render(surface, self.camera)

        if self.aiming:
            self._render_pull_line(surface)

        render_text(surface, HUD_TEXT, settings.FONTS["small"], 10, 10, (70, 55, 40))

    def _render_pull_line(self, surface: pygame.Surface) -> None:
        start = self.camera.world_to_screen(self.bird.initial_position)
        end = self.camera.world_to_screen(self.bird.position)
        pygame.draw.line(surface, (110, 75, 40), start, end, 3)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "touch":
            self._on_touch(input_data)
        elif input_id == "touch_motion":
            self._on_touch_motion(input_data)
        elif input_id == "split" and input_data.pressed:
            self._split_bird()

    def _split_bird(self) -> None:
        # Only the blue bird carries the split power-up, and only while
        # it is actually in flight, hasn't hit anything yet (spec 2), and
        # hasn't already split this throw (powerup_activated).
        bird = self.bird

        if (
            not self.flinging
            or bird.color != "blue"
            or bird.has_collided
            or bird.powerup_activated
        ):
            return

        bird.powerup_activated = True
        velocity = bird.body.velocity

        for angle in (-SPLIT_ANGLE_DEGREES, SPLIT_ANGLE_DEGREES):
            heading = velocity.rotate(angle)

            # Spawned at the center bird's own position, then pushed out
            # along its own heading, not left stacked on top of it/each
            # other -- see the SPLIT_SPAWN_OFFSET_RADII comment.
            split_bird = Bird(self.world, bird.position.x, bird.position.y, color=bird.color)
            offset = heading.normalize() if heading.length() > 0 else pygame.Vector2(1, 0)
            split_bird.body.position = (
                bird.position + offset * split_bird.radius * SPLIT_SPAWN_OFFSET_RADII
            )
            split_bird.body.velocity = heading
            split_bird.body.angular_velocity = bird.body.angular_velocity
            split_bird.body.angle = bird.body.angle
            split_bird.powerup_activated = True
            self.birds.append(split_bird)

    def _mouse_to_virtual(self, position) -> pygame.Vector2:
        scale_x = settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH
        scale_y = settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT
        return pygame.Vector2(position[0] * scale_x, position[1] * scale_y)

    def _on_touch(self, input_data: InputData) -> None:
        position = self._mouse_to_virtual(input_data.position)

        if input_data.pressed:
            self.pressed_position = position
            world_position = pygame.Vector2(self.camera.screen_to_world(position))

            if (
                not self.flinging
                and (world_position - self.bird.position).length() < AIM_GRAB_RADIUS
            ):
                self.aiming = True
                self.aim_offset = pygame.Vector2()
            else:
                self.panning = True
                self.pressed_camera_target = pygame.Vector2(self.camera_target)
        elif input_data.released:
            if self.aiming:
                self._fling()

            self.aiming = False
            self.panning = False

    def _fling(self) -> None:
        pull = self.bird.initial_position - self.bird.position
        if pull.length() < 5:
            self.bird.reset()
            return
        # Scaled by the bird's own mass so it cancels out of the
        # resulting delta-v -- see the FLING_IMPULSE_SCALE docstring.
        scale = FLING_IMPULSE_SCALE * self.bird.mass
        self.bird.body.apply_impulse(pull.x * scale, pull.y * scale)
        self.flinging = True
        self.idle_frames = 0

    def _on_touch_motion(self, input_data: InputData) -> None:
        if not (self.aiming or self.panning):
            return

        position = self._mouse_to_virtual(input_data.position)
        # Screen-space delta since the press, converted to world units by
        # dividing out the camera's current zoom.
        screen_delta = self.pressed_position - position
        world_delta = screen_delta / self.camera.zoom

        if self.aiming:
            if world_delta.length() > MAX_PULL_DISTANCE:
                world_delta.scale_to_length(MAX_PULL_DISTANCE)

            # Just remember the offset; update()'s _hold_bird_while_aiming
            # re-applies it (and zeroes velocity) every frame, not only on
            # the frames a motion event happens to arrive.
            self.aim_offset = world_delta
        elif self.panning:
            target = self.pressed_camera_target + world_delta
            left, right = self.level.ground_x_range
            target.x = max(
                left - CAMERA_PAN_MARGIN, min(right + CAMERA_PAN_MARGIN, target.x)
            )
            self.camera_target.update(target)
