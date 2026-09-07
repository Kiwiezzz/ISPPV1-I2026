import random
from typing import Any, Callable, List, Optional, TypeVar

import pygame

from gale.tilemap import TileMap

import settings
from src.definitions.entity import ENTITY_DEFS
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.Entity import Entity
from src.GameObject import GameObject
from src.states.entity.EntityIdleState import EntityIdleState
from src.states.entity.EntityWalkState import EntityWalkState
from typing import Any, Callable, TypeVar

import pygame
from gale.timer import Timer
from gale.input_handler import InputHandler

import settings
from src.Bow import Bow
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.GameObject import GameObject
from src.world.Room import Room

class ChestRoom(Room):
    def __init__(self, player: TypeVar("Player"), on_game_over: Callable[[], None]) -> None:
        super().__init__(player, on_game_over)
        self.chest_opened: bool = False
        self.during_animation: bool = False
        self.fake_bow: GameObject = None 
        #This resolve an animation bug when de player collides with chest
        self._saved_player_pos: Optional[tuple[float, float]] = None

        for doorway in self.doorways:
            doorway.open = True

    def _generate_entities(self) -> None:
        pass 

    def _generate_objects(self) -> None:
        chest_def = GAME_OBJECT_DEFS["chest"]
        chest_x = (settings.VIRTUAL_WIDTH / 2) - (chest_def["width"] / 2)
        chest_y = (settings.VIRTUAL_HEIGHT / 2) - (chest_def["height"] / 2)
        
        self.objects.append(GameObject(chest_def, chest_x, chest_y))

    def update(self, dt: float) -> None:
        # Keep doors open since there are no switches or enemies in the chest room
        for doorway in self.doorways:
            doorway.open = True

        if self.during_animation:
            if self.player.current_animation:
                self.player.current_animation.update(dt)
            
            if getattr(self.player.state_machine.current, "pot", None) == self.fake_bow:
                self.player.interact_requested = False
            return

        if getattr(self.player, "interact_requested", False) and not self.chest_opened:

            chest = self.objects[0] 

            # Player looking to chest logic
            player_y = self.player.y + self.player.height / 2
            player_height = self.player.height - self.player.height / 2
            player_col = int((self.player.x + self.player.width / 2) // settings.TILE_SIZE)
            player_row = int((player_y + player_height / 2) // settings.TILE_SIZE)
            
            chest_left_col = int(chest.x // settings.TILE_SIZE)
            chest_right_col = int((chest.x + chest.width - 1) // settings.TILE_SIZE)
            chest_row = int((chest.y + chest.height / 2) // settings.TILE_SIZE)

            if self.player.direction == "up" and chest_left_col <= player_col <= chest_right_col and chest_row == player_row - 1:
                #fix player position during animation
                self._saved_player_pos = (self.player.x + 0.1, self.player.y + 0.1)
                self.player.interact_requested = False               
                self._opening_chest()


                return

        super().update(dt)
        

    def _opening_chest(self) -> None:

        """
        For this animation I decided not to use tween on the fake bow because 
        I am reusing already implemented functions such as lifting an object 
        (reused from the PlayerPotLiftState finite state machine which already 
        uses a Tween)
        """

        self.chest_opened = True
        self.during_animation = True
        
        chest = self.objects[0]
        chest.state = "opened"
        
        settings.SOUNDS["chest_open"].play()
            
        self.player.change_state("idle")
        self.player.direction = "up"
        
        def raising_the_bow():
            bow_def = {
                "type": "bow_item",
                "texture": "bow",
                "frame": 1,
                "width": 16,
                "height": 16,
                "solid": False,
                "default_state": "default",
                "states": {"default": {"texture": "bow", "frame": 1}}
            }
            self.fake_bow = GameObject(bow_def, self.player.x, self.player.y)
            
            self.player.change_state("pot-lift", pot=self.fake_bow)
            
            def change_direction():
                self.player.direction = "down"
                self.player.change_animation("pot-idle-down")
            
            #I wanted to do it with a lambda function, but it was a less readable code
            Timer.after(0.1, change_direction)
            
            def return_to_normal():
                self.player.change_state("idle")
                self.fake_bow = None
                self.during_animation = False
                self.player.bow = Bow()
                self.player.x, self.player.y = self._saved_player_pos
                self._saved_player_pos = None
                
            Timer.after(3.0, return_to_normal)

        Timer.after(7.5, raising_the_bow)

    def render(self, surface: pygame.Surface, camera_offset_x: float = 0, camera_offset_y: float = 0) -> None:
        super().render(surface, camera_offset_x, camera_offset_y)
        
        #During animation render fake_bow
        if self.fake_bow:
            offset_x = self.adjacent_offset_x + camera_offset_x
            offset_y = self.adjacent_offset_y + camera_offset_y
            self.fake_bow.render(surface, offset_x, offset_y)