"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from src.FlyingCreature import FlyingCreature
from src.states.entities import creatures_states
from src import commands
from typing import Dict, Any

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Clock import Clock
from src.GameLevel import GameLevel
from src.Player import Player


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params.get("level", 1)
        self.game_level = enter_params.get("game_level")
        if self.game_level is None:
            self.game_level = GameLevel(self.level)
            pygame.mixer.music.load(
                settings.BASE_DIR / "assets" / "sounds" / "music_grassland.ogg"
            )
            pygame.mixer.music.play(loops=-1)

        self.tilemap = self.game_level.tilemap
        self.player = enter_params.get("player")
        if self.player is None:
            # Resting exactly on the ground tile's surface (row 9, one tile
            # below the platform's top edge) rather than a few pixels into
            # it, so gale.tilemap's one-way platform collision (which
            # requires the entity to already be at/above the surface) picks
            # it up on the very first frame instead of falling through.
            spawn_y = 9 * self.tilemap.tile_height - 20
            self.player = Player(0, spawn_y, self.game_level)
            self.player.change_state("idle")

        self.camera = enter_params.get("camera")

        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.game_level.get_rect()
            self.camera.x, self.camera.y = self.player.x, self.player.y
            self.camera.update(0)

        self.clock = enter_params.get("clock")

        if self.clock is None:
            self.clock = Clock(150)

            def countdown_timer():
                self.clock.count_down()

                if 0 < self.clock.time <= 5:
                    settings.SOUNDS["timer"].play()

                if self.clock.time == 0:
                    self.player.change_state("dead")

            Timer.every(1, countdown_timer)
        else:
            Timer.resume()

        # Overlay used for the fade-in (on enter) and fade-out (on key collect) transitions
        self.fade_overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self.fade_alpha = 255  # Start fully black, tween down to 0 for the fade-in
        self.transitioning = False  # Guard: only one transition at a time
        self.is_victory = False     # True once the score target is reached

        Timer.tween(
            0.5,
            [(self, {"fade_alpha": 0})],
            ease_function_name="in_cubic",
        )

        # Scan the ground layer for the is_key tile, store its location and
        # original gid, then hide it by zeroing that cell so the block only
        # appears once the player reaches the score target.
        self._key_block_row = None
        self._key_block_col = None
        self._key_block_gid = None

        for row in range(self.tilemap.rows):
            for col in range(self.tilemap.cols):
                gid = self.tilemap.get_gid("ground", row, col)
                if self.tilemap.properties_of_gid(gid).get("is_key", False):
                    self._key_block_row = row
                    self._key_block_col = col
                    self._key_block_gid = gid
                    # Hide the block until the score target is reached
                    self.tilemap.set_gid("ground", row, col, 0)
                    break
            if self._key_block_gid is not None:
                break

    def update(self, dt: float) -> None:
        
        if(self.level == settings.NUM_LEVELS and self.player.score >= settings.KEY_SCORE_TARGET and not self.transitioning):
            self._begin_level_transition()
        
        if self.player.is_dead:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            Timer.clear()
            self.state_machine.change("game_over", self.player)

        self.player.update(dt)

        if self.player.y >= self.tilemap.pixel_height:
            self.player.change_state("dead")

        self.camera.update(dt)
        self.game_level.update(dt)

        # Creature collisions are disabled after victory
        if not self.is_victory:
            for creature in self.game_level.creatures:
                if self.player.collides(creature):

                    # introduce stomp like in a certain game by a company I can't mention
                    if (self.player.vy > 0 and
                            self.player.y + self.player.height <= creature.y + creature.height / 2):
                        if isinstance(creature, FlyingCreature):
                            creature.change_state("fall")
                            self.player.score += 50
                        else:
                            # Ground snail go hidden on first stomp instead of dying
                            creature.change_state("hidden")
                        self.player.vy = -settings.JUMP_CUT_VELOCITY  # small bounce
                    else:
                        # It eliminates the damage if the creatine is hidden or falling out
                        is_neutralized = isinstance(
                            creature.state_machine.current,
                            (creatures_states.FlyingFallState, creatures_states.SnailHiddenState),
                        )
                        if not is_neutralized:
                            self.player.change_state("dead")

        # Reveal the key block once the score target is reached
        if (
            not self.is_victory
            and self._key_block_gid is not None
            and self.player.score >= settings.KEY_SCORE_TARGET
        ):
            self.is_victory = True
            self.tilemap.set_gid(
                "ground",
                self._key_block_row,
                self._key_block_col,
                self._key_block_gid,
            )
            Timer.clear() 

        # Coin collection is disabled after victory; the Key is still collidable
        for item in self.game_level.items:
            if not item.active or not item.collidable:
                continue

            is_key = getattr(item, "spawn_y", None) is not None

            if self.is_victory and not is_key:
                continue  # Pass through all coins after victory

            if self.player.collides(item):
                item.on_collide(self.player)
                item.on_consume(self.player)

                if is_key and not self.transitioning:
                    self._begin_level_transition()

    def _begin_level_transition(self) -> None:

        self.transitioning = True
        settings.SOUNDS["victory"].play()
        self.player.change_state("idle")
        commands.STOP_MOVE_LEFT.execute(self.player)
        commands.STOP_MOVE_RIGHT.execute(self.player)
        Timer.clear()

        Timer.tween(
            3.5,
            [(self, {"fade_alpha": 255})],
            ease_function_name="linear",
            on_finish=self._go_to_next_level,
        )

    def _go_to_next_level(self) -> None:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        if self.level == settings.NUM_LEVELS:
            self.state_machine.change("game_over", self.player)
        else:
            self.state_machine.change("play", level=self.level + 1)

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)

        render_text(
            surface,
            f"Score: {self.player.score}/{settings.KEY_SCORE_TARGET}",
            settings.FONTS["small"],
            5,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        render_text(
            surface,
            f"Time: {self.clock.time}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH - 60,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        # Draw the fade overlay on top of everything
        if self.fade_alpha > 0:
            self.fade_overlay.fill((0, 0, 0, int(self.fade_alpha)))
            surface.blit(self.fade_overlay, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            Timer.pause()
            self.state_machine.change(
                "pause",
                level=self.level,
                camera=self.camera,
                game_level=self.game_level,
                player=self.player,
                clock=self.clock,
            )
        else:
            if(not self.transitioning):
                self.player.on_input(input_id, input_data)
