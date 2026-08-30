"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""

import random

import pygame

from gale.factory import AbstractFactory
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
import src.powerups
from src.Rocket import Rocket


class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])
        self.rockets = params.get("rockets", [])
        self.cannons_powerup = params.get("cannons_powerup", None)
        self.catch_powerup = params.get("catch_powerup", None)
        self.caught_ball = params.get("caught_ball", None)
        self.ball_offset_x = params.get("ball_offset_x", 0)
        self.bomb_powerup = params.get("bomb_powerup", None)

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

    def update(self, dt: float) -> None:
        self.paddle.update(dt)

        for ball in self.balls:
            if ball is self.caught_ball:
                r = self.paddle.get_collision_rect()
                ball.x = r.x + self.ball_offset_x
                ball.y = r.y - ball.height
                continue

            ball.update(dt)
            ball.solve_world_boundaries()

            if ball.collides(self.paddle):
                if (self.catch_powerup is not None
                        and self.catch_powerup.active_powerup
                        and self.caught_ball is None):
                    r = self.paddle.get_collision_rect()
                    self.ball_offset_x = ball.x - r.x
                    self.caught_ball = ball
                    ball.vx = 0
                    ball.vy = 0
                else:
                    settings.SOUNDS["paddle_hit"].stop()
                    settings.SOUNDS["paddle_hit"].play()
                    ball.rebound(self.paddle)
                    ball.push(self.paddle)

            # Check collision with brickset
            if not ball.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(ball.get_collision_rect())

            if brick is None:
                continue

            bomb_active = self.bomb_powerup is not None and self.bomb_powerup.active_powerup
            brick.hit(play_sound=not bomb_active)
            self.score += brick.score()
            ball.rebound(brick)
            
            # Ensure that the block that hits the ball receives double damage
            if bomb_active:
                settings.SOUNDS["bomb"].stop()
                settings.SOUNDS["bomb"].play()
                if not brick.broken:
                    brick.hit(play_sound=False)
                    self.score += brick.score()

                br = brick.get_collision_rect()
                hit_row = (br.y - self.brickset.collision_rect.y) // 16
                hit_col = (br.x - self.brickset.collision_rect.x) // 32
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i == 0 and j == 0:
                            continue
                        neighbor = self.brickset.get_brick(hit_row + i, hit_col + j)
                        if neighbor is not None and not neighbor.broken:
                            neighbor.hit(play_sound=False)
                            self.score += neighbor.score()
                            # This is designed to take down two tiers in one hit while the power-up is active
                            if not neighbor.broken:
                                neighbor.hit(play_sound=False)
                                self.score += neighbor.score()


            # Check earn life
            if self.score >= self.points_to_next_live:
                settings.SOUNDS["life"].play()
                self.lives = min(3, self.lives + 1)
                self.live_factor += 0.5
                self.points_to_next_live += settings.LIVE_POINTS_BASE * self.live_factor

            # Check growing up of the paddle
            if self.score >= self.points_to_next_grow_up:
                settings.SOUNDS["grow_up"].play()
                self.points_to_next_grow_up += (
                    settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
                )
                self.paddle.inc_size()

            # Random chance of generating a powerup
            if random.random() < 0.1:
                powerup_name = random.choice(settings.POWERUP_TYPES)
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory(powerup_name).create(
                        r.centerx - 8, r.centery - 8
                    )
                )

        # Removing all balls that are not in play
        self.balls = [ball for ball in self.balls if ball.active]

        self.brickset.update(dt)

        if not self.balls:
            self.lives -= 1
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                self.paddle.dec_size()
                self.state_machine.change(
                    "serve",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                )

        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)

            if powerup.collides(self.paddle):
                powerup.take(self)

        self.powerups = [p for p in self.powerups if p.active]

        if self.catch_powerup is not None and self.catch_powerup.active_powerup:
            self.catch_powerup.update(dt)
            if not self.catch_powerup.active_powerup:
                if self.caught_ball is not None:
                    self.caught_ball.vx = random.randint(-80, 80)
                    self.caught_ball.vy = random.randint(-170, -100)
                    self.caught_ball = None
                self.catch_powerup = None

        if self.bomb_powerup is not None and self.bomb_powerup.active_powerup:
            self.bomb_powerup.update(dt)
            if not self.bomb_powerup.active_powerup:
                self.bomb_powerup = None

        if self.cannons_powerup is not None and self.cannons_powerup.active_powerup:
            self.cannons_powerup.update(dt)
            if not self.cannons_powerup.active_powerup:
                self.cannons_powerup = None

        # Update rockets
        for rocket in self.rockets:
            rocket.update(dt)

            # It collides with the brickset, destroys the brick in question,
            # and then the rocket self-destructs
            if rocket.collides(self.brickset):
                brick = self.brickset.get_colliding_brick(rocket.get_collision_rect())
                if brick is not None and not brick.broken:
                    brick.hit()
                    self.score += brick.score()
                    rocket.active = False  

        # Remove rockets that are not in play
        self.rockets = [r for r in self.rockets if r.active]

        # Check victory
        if self.brickset.size > 0 and all(b.broken for b in self.brickset.bricks.values()):
            self.state_machine.change(
                "victory",
                lives=self.lives,
                level=self.level,
                score=self.score,
                paddle=self.paddle,
                balls=self.balls,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
            )

    def render(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )

        self.brickset.render(surface)

        self.paddle.render(surface)

        for ball in self.balls:
            ball.render(surface)

        for powerup in self.powerups:
            powerup.render(surface)

        if self.cannons_powerup is not None:
            self.cannons_powerup.render(surface)

        for rocket in self.rockets:
            rocket.render(surface)

        BAR_W = 60
        BAR_H = 5
        x0 = 4
        y0 = 5
        slot = 0
        for label, powerup in [
            ("CatchTheBall", self.catch_powerup),
            ("Cannons", self.cannons_powerup),
            ("Bomb", self.bomb_powerup),
        ]:
            if powerup is None or not powerup.active_powerup:
                continue
            y = y0 + slot * 18
            render_text(surface, label, settings.FONTS["tiny"], x0, y, (255, 255, 255))
            bar_y = y + 8
            remaining = max(0.0, 1.0 - powerup.timer / powerup.DURATION)
            pygame.draw.rect(surface, (255, 255, 255), (x0 - 1, bar_y - 1, BAR_W + 2, BAR_H + 2), 1)
            pygame.draw.rect(surface, (50, 205, 50), (x0, bar_y, int(BAR_W * remaining), BAR_H))
            slot += 1


    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_left":
            if input_data.pressed:
                self.paddle.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx < 0:
                self.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.paddle.vx = settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx > 0:
                self.paddle.vx = 0
        elif input_id == "pause" and input_data.pressed:
            if self.caught_ball is not None:
                self.caught_ball.vx = random.randint(-80, 80)
                self.caught_ball.vy = random.randint(-170, -100)
                self.caught_ball = None
            else:
                self.state_machine.change(
                    "pause",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    balls=self.balls,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                    powerups=self.powerups,
                    rockets=self.rockets,
                    cannons_powerup=self.cannons_powerup,
                    catch_powerup=self.catch_powerup,
                    caught_ball=self.caught_ball,
                    ball_offset_x=self.ball_offset_x,
                    bomb_powerup=self.bomb_powerup,
                )
        elif input_id == "fire" and input_data.pressed:
            # Fire only if there are active cannons and no rockets in flight
            if self.cannons_powerup is not None and self.cannons_powerup.active_powerup and len(self.rockets) == 0:
                settings.SOUNDS["cannon"].stop()
                settings.SOUNDS["cannon"].play()
                r = self.paddle.get_collision_rect()
                self.rockets.append(Rocket(r.left - 4, r.y - 16, flipped=True))
                self.rockets.append(Rocket(r.right - 4, r.y - 16, flipped=False))
