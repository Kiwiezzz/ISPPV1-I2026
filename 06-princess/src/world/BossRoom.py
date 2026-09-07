from typing import Callable, List, TypeVar

import pygame

import settings
from src.definitions.entity import ENTITY_DEFS
from src.Entity import Entity
from src.Fireball import Fireball
from src.states.entity.BossIdleState import BossIdleState
from src.states.entity.BossInvertedState import BossInvertedState
from src.states.entity.BossWalkState import BossWalkState
from src.world.Room import Room

_FIRE_INTERVAL = 2.5

_OPPOSITE = {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}


class BossRoom(Room):
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
        entrance_direction: str = "left",
    ) -> None:
        self.entrance_direction = entrance_direction
        self.boss = None
        self.fireballs: List[Fireball] = []
        self.fire_timer = 0.0
        self._boss_defeated = False
        super().__init__(player, on_game_over)

        # Only the doorway the player came in through exists; the other
        # three sides are solid wall.
        entrance = self._doorways_by_direction[entrance_direction]
        self.doorways = [entrance]
        self._doorways_by_direction = {entrance_direction: entrance}

    def _generate_entities(self) -> None:
        definition = ENTITY_DEFS["boss"]
        spawn_x, spawn_y = self._boss_spawn_position()

        boss = Entity(
            x=spawn_x,
            y=spawn_y,
            width=32,
            height=32,
            # Deliberately faster than the player (60) and normal enemies.
            walk_speed=definition.get("walk_speed", 90),
            health=24,
            animation_defs=definition["animations"],
            states={},
        )

        # Immune to the sword unless an arrow has knocked it into its
        # inverted (vulnerable) state; always damageable by arrows.
        boss.sword_vulnerable = False

        # Touching the boss body costs the player a full heart (2 health).
        boss.contact_damage = 2

        boss.state_machine.states = {
            "idle": lambda sm, e=boss: BossIdleState(e, sm),
            "walk": lambda sm, e=boss: BossWalkState(e, sm),
            "inverted": lambda sm, e=boss: BossInvertedState(e, sm),
        }
        boss.change_state("walk")
        self.boss = boss
        self.entities.append(boss)

    def _generate_objects(self) -> None:
        pass

    def _boss_spawn_position(self) -> tuple:
        boss_size = 32
        left = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
        right = settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - boss_size
        top = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE
        bottom = (
            settings.MAP_HEIGHT * settings.TILE_SIZE
            + settings.MAP_RENDER_OFFSET_Y
            - settings.TILE_SIZE
            - boss_size
        )
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2

        side = _OPPOSITE[self.entrance_direction]

        if side == "left":
            return left, center_y
        if side == "right":
            return right, center_y
        if side == "top":
            return center_x, top
        return center_x, bottom

    def update(self, dt: float) -> None:
        super().update(dt)

        # Room is mid screen-shift: freeze the fight too.
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        self._update_fireballs(dt)
        self._update_boss_attack(dt)
        self._check_boss_defeated()

    def _update_boss_attack(self, dt: float) -> None:
        if self.boss is None or self.boss.dead or self.boss.sword_vulnerable:
            return

        self.fire_timer += dt

        if self.fire_timer >= _FIRE_INTERVAL:
            self.fire_timer = 0.0
            self.fireballs.append(
                Fireball(
                    self.boss.x + self.boss.width / 2,
                    self.boss.y + self.boss.height / 2,
                    self.player.x + self.player.width / 2,
                    self.player.y + self.player.height / 2,
                )
            )

    def _update_fireballs(self, dt: float) -> None:
        for fireball in list(self.fireballs):
            fireball.update(dt)

            if fireball.collides(self.player):
                settings.SOUNDS["hit-player"].play()
                self.player.health = 0
                fireball.dead = True
                self.on_game_over()

            if fireball.dead:
                self.fireballs.remove(fireball)

    def _check_boss_defeated(self) -> None:
        if self._boss_defeated or self.boss is None or not self.boss.dead:
            return

        self._boss_defeated = True

        for doorway in self.doorways:
            doorway.open = True

        settings.SOUNDS["door"].play()

    def render(
        self,
        surface: pygame.Surface,
        camera_offset_x: float = 0,
        camera_offset_y: float = 0,
    ) -> None:
        super().render(surface, camera_offset_x, camera_offset_y)

        for fireball in self.fireballs:
            fireball.render(surface, camera_offset_x, camera_offset_y)
