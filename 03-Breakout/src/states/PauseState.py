import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings


class PauseState(BaseState):
    def enter(self, **params: dict) -> None:
        self.level = params["level"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.powerups = params["powerups"]
        self.rockets = params["rockets"]
        self.cannons_powerup = params["cannons_powerup"]
        self.catch_powerup = params["catch_powerup"]
        self.caught_ball = params["caught_ball"]
        self.ball_offset_x = params["ball_offset_x"]
        self.bomb_powerup = params["bomb_powerup"]
        settings.SOUNDS["pause"].play()

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

        render_text(
            surface,
            "Pause",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2,
            (255, 255, 255),
            center=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "play",
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
                resume=True,
            )
