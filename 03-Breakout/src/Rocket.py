from typing import Any

import pygame

import settings


class Rocket:
    SPEED = 200

    def __init__(self, x: int, y: int, flipped: bool = False) -> None:
        self.x = x
        self.y = y
        self.width = 8
        self.height = 16
        self.vy = -Rocket.SPEED
        self.active = True
        self.flipped = flipped

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collides(self, obj: Any) -> bool:
        return self.get_collision_rect().colliderect(obj.get_collision_rect())

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y + self.height < 0:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        frame_rect = settings.FRAMES["powerups"][11]
        sprite = settings.TEXTURES["spritesheet"].subsurface(frame_rect)
        if self.flipped:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (self.x, self.y))
