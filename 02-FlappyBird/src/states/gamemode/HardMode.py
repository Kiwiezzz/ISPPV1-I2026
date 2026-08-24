from src import Bird
from src import Bird
import pygame
import random

from gale.input_handler import InputData
from gale.text import render_text
from gale.factory import Factory

import settings
from src.Bird import Bird
from src.World import World
from .GameMode import GameMode
from src.LogPair import LogPair
from src.MovingLogPair import MovingLogPair
from src.PowerUp import PowerUp

class HardMode(GameMode):

    def __init__(self, generate_logs: bool = False) -> None:
        self.generate_logs: bool = generate_logs
        self.logs_spawn_timer = 0.0
        self.last_log_y = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        self.current_spawn_interval = random.uniform(1.2, 2.5)
        self.log_pair_factory: Factory = Factory(LogPair)
        self.powerup_factory: Factory = Factory(PowerUp)
        self.is_ghost_active = False
        self.ghost_timer = 0.0
        self.powerup_spawn_timer = 0.0
        self.current_powerup_interval = random.uniform(8.0, 12.0)

    def reset(self, generate_logs: bool) -> None:
        self.generate_logs = generate_logs
        self.logs_spawn_timer = 0.0
        self.last_log_y = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        
        self.powerup_spawn_timer = 0.0
        self.current_powerup_interval = random.uniform(8.0, 12.0)
        
        # Reset ghost state in case he died with it active
        if self.is_ghost_active:
            pygame.mixer.music.load(settings.BACKGROUND_MUSIC)
            pygame.mixer.music.play(-1)
        self.is_ghost_active = False
        self.ghost_timer = 0.0
        settings.TEXTURES["bird"].set_alpha(255)
        
    def update(self, dt: float, bird: Bird, world: World) -> None:
      
        if self.is_ghost_active:
            self.ghost_timer += dt
            if self.ghost_timer >= settings.TIME_POWERUP - 2:
                if int(self.ghost_timer * 10) % 2 == 0:
                    settings.TEXTURES["bird"].set_alpha(255)
                else:
                    settings.TEXTURES["bird"].set_alpha(128)
            else:
                settings.TEXTURES["bird"].set_alpha(128)

            if self.ghost_timer >= settings.TIME_POWERUP:
                self.is_ghost_active = False
                settings.TEXTURES["bird"].set_alpha(255)
                pygame.mixer.music.load(settings.BACKGROUND_MUSIC)
                pygame.mixer.music.play(-1)
        

        bird_rect = bird.get_rect()

        # The list of active power-ups is copied for safe deletion
        for powerup in world.powerups[:]: 
            if powerup.collides(bird_rect):
                if not self.is_ghost_active:
                    settings.SOUNDS["powerup"].stop()    
                world.powerups.remove(powerup)
                self.is_ghost_active = True
                self.ghost_timer = 0.0
                settings.TEXTURES["bird"].set_alpha(128)
                settings.SOUNDS["powerup"].play()
                pygame.mixer.music.load(settings.MUSIC_GHOST)
                pygame.mixer.music.play(-1)



        if self.generate_logs:
            self.logs_spawn_timer += dt
            
            if self.logs_spawn_timer >= self.current_spawn_interval:
                self.logs_spawn_timer = 0.0
                max_y_change = int((self.current_spawn_interval - 1.0) * 80) 
                
                # Dynamic gap
                gap = random.randint(75, 115)
                
                y = max(
                    -settings.LOG_HEIGHT + 10,
                    min(
                        self.last_log_y + random.randint(-max_y_change, max_y_change),
                        settings.VIRTUAL_HEIGHT - gap - settings.LOG_HEIGHT - 10,
                    ),
                )
                self.last_log_y = y
                gap = random.randint(75, 100)
                
                if random.random() > 0.4:
                    log_pair = MovingLogPair(settings.VIRTUAL_WIDTH, y, gap=gap)
                else:
                    log_pair = LogPair(settings.VIRTUAL_WIDTH, y, gap=gap)



                world.add_log(log_pair)
                self.current_spawn_interval = random.uniform(1.6, 2.5)
        
            self.powerup_spawn_timer += dt
            if self.powerup_spawn_timer >= self.current_powerup_interval and  random.random() > 0.5:
                self.powerup_spawn_timer = 0.0
                self.current_powerup_interval = random.uniform(8.0, 15.0)
                
                min_y = 20
                max_y = settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT - settings.POWERUP_HEIGHT - 20
                powerup_y = random.randint(min_y, max_y)
                
                world.add_powerup(self.powerup_factory.create(settings.VIRTUAL_WIDTH, powerup_y))

        bird.update(dt)
        world.update(dt)

    def is_game_over(self, bird: Bird, world: World) -> bool:
        rect = bird.get_rect()

        if rect.bottom >= settings.VIRTUAL_HEIGHT:
            return True
            
        if self.is_ghost_active:
            return False
            
        for log_pair in world.logs:
            if log_pair.collides(rect):
                return True

        return False

    def on_score(self, bird: Bird, world: World) -> bool:
        return world.update_scored(bird.get_rect())

    def render(self, surface: pygame.Surface, score: int) -> None:
        render_text(
            surface,
            f"Score: {score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData, bird: Bird) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()
        elif input_id == "a":
            if input_data.pressed:
                bird.vx = -settings.BIRD_SPEED
            elif bird.vx < 0:
                bird.vx = 0
        elif input_id == "d":
            if input_data.pressed:
                bird.vx = settings.BIRD_SPEED
            elif bird.vx > 0:
                bird.vx = 0
