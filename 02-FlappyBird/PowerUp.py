import pygame

import settings

class PowerUp:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), settings.POWERUP_WIDTH, settings.POWERUP_HEIGHT)

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_rect().colliderect(rect)
    
    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

    def is_out_of_game(self) -> bool:
        return self.x < -settings.POWERUP_WIDTH

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["powerup"], self.get_rect())