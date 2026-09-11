import random
from typing import Any, Callable, List, Optional, Tuple

import pygame

from gale.state import BaseState
from gale.tilemap import TileMap
from gale.timer import Timer

import settings
from src.definitions.entity import BATTLE_HEIGHT, BATTLE_PADDLE, BATTLE_WIDTH

INTERIOR_TILE_IDS = settings.INTERIOR_TILE_IDS


class GuildHallState(BaseState):
    def enter(self, party: Any, on_exit: Callable[[], None]) -> None:
        self.party = party
        self.on_exit = on_exit
        self.moving = False
        self.held = {
            "move_left": False,
            "move_right": False,
            "move_up": False,
            "move_down": False,
        }

        self.width = BATTLE_WIDTH
        self.height = BATTLE_HEIGHT
        self.door = {"x": self.width // 2, "y": self.height}

        # (row, col) -> True for every non-walkable cell (border walls and
        # furniture footprints). Kept separate from the tilemap itself so
        # collision never depends on which gids happen to be "solid
        # looking" -- unlike the overworld's fence layer, nothing here
        # needs to double as a rendered tile.
        self.solid: List[List[bool]] = [
            [False] * self.width for _ in range(self.height)
        ]

        self.tilemap = TileMap(
            settings.TILE_SIZE, settings.TILE_SIZE, self.width, self.height
        )
        self.tilemap.add_tileset(settings.INTERIOR_TILESET)
        self._create_map()
        self._place_party()

    def exit(self) -> None:
        self.on_exit()

    def _place_party(self) -> None:
        # Lined up horizontally (not "up", i.e. vertically, like the
        # overworld's own gate entrances use): stacked vertically, 4
        # characters would run past the bottom wall in a room this short.
        # The row just past the door has the full width to grow into.
        self.party.set_position(self.door["x"], self.door["y"] - 1, "left")

        # One bed per possible party slot: a dead character shows up
        # resting on their own bed instead of walking around with the
        # rest of the party.
        keys = sorted(self.party.characters.keys())
        for index, key in enumerate(keys):
            character = self.party.characters[key]

            if character.dead:
                bed = self.bed_positions[index]
                character.map_x = bed["x"]
                character.map_y = bed["y"]
                character.x = (character.map_x - 1) * settings.TILE_SIZE
                character.y = (
                    character.map_y - 1
                ) * settings.TILE_SIZE - character.height / 2
                character.direction = "down"

            character.change_state("idle")

    def _create_map(self) -> None:
        floor = self.tilemap.add_layer("floor")
        for y in range(self.height):
            for x in range(self.width):
                floor[y][x] = random.choice(INTERIOR_TILE_IDS["floor"])

        # Border wall, one tile thick, using the same 8-piece corner/edge
        # scheme as Region's own fence layer (top-left/top/top-right,
        # left/right, bottom-left/bottom/bottom-right -- no "center" piece
        # needed since the wall is never more than one tile deep).
        walls = self.tilemap.add_layer("walls")
        for y in range(self.height):
            for x in range(self.width):
                if y == 0:
                    if x == 0:
                        tile_id = INTERIOR_TILE_IDS["top-left-wall"]
                    elif x == self.width - 1:
                        tile_id = INTERIOR_TILE_IDS["top-right-wall"]
                    else:
                        tile_id = INTERIOR_TILE_IDS["top-wall"]
                elif y == self.height - 1:
                    if x == 0:
                        tile_id = INTERIOR_TILE_IDS["bottom-left-wall"]
                    elif x == self.width - 1:
                        tile_id = INTERIOR_TILE_IDS["bottom-right-wall"]
                    else:
                        tile_id = INTERIOR_TILE_IDS["bottom-wall"]
                elif x == 0:
                    tile_id = INTERIOR_TILE_IDS["left-wall"]
                elif x == self.width - 1:
                    tile_id = INTERIOR_TILE_IDS["right-wall"]
                else:
                    continue

                self.solid[y][x] = True
                walls[y][x] = tile_id

        # The door is a walkable gap in the bottom wall.
        door_row, door_col = self.door["y"] - 1, self.door["x"] - 1
        self.solid[door_row][door_col] = False
        walls[door_row][door_col] = 0

        # 4 beds, evenly spaced along the top wall -- one per party slot.
        self.bed_positions: List[dict] = []
        beds = self.tilemap.add_layer("beds")

        for bed_x in (2, 6, 10, 14):
            bed_y = 2
            self.bed_positions.append({"x": bed_x, "y": bed_y})
            self._place(beds, INTERIOR_TILE_IDS["bed"], bed_x, bed_y)

    def _place(self, layer: List[List[int]], block: List[List[int]], x: int, y: int) -> None:
        """x, y are 1-based tile coordinates of the block's top-left cell."""
        for dy, row in enumerate(block):
            for dx, gid in enumerate(row):
                layer[y - 1 + dy][x - 1 + dx] = gid
                self.solid[y - 1 + dy][x - 1 + dx] = True

    @staticmethod
    def _delta(direction: str) -> Tuple[int, int]:
        if direction == "left":
            return -1, 0
        elif direction == "right":
            return 1, 0
        elif direction == "up":
            return 0, -1
        else:
            return 0, 1

    def _next_alive_ahead(self, order: List[int], i: int) -> Optional[int]:
        for j in reversed(order):
            if j < i and not self.party.characters[j].dead:
                return j

        return None

    def _attempt_move(self, direction: str) -> None:
        characters = self.party.characters
        order = sorted(characters.keys())
        first = self.party.first_alive_position()

        if first is None:
            return

        for i in reversed(order):
            if i <= first or characters[i].dead:
                continue

            j = self._next_alive_ahead(order, i)

            if j is None:
                continue

            follower, ahead = characters[i], characters[j]

            if follower.map_x < ahead.map_x:
                follower.direction = "right"
            elif follower.map_x > ahead.map_x:
                follower.direction = "left"
            elif follower.map_y < ahead.map_y:
                follower.direction = "down"
            elif follower.map_y > ahead.map_y:
                follower.direction = "up"

            follower.change_state("walk")

        leader = characters[first]
        leader.direction = direction
        leader.change_state("walk")

        dx, dy = self._delta(direction)
        to_x, to_y = leader.map_x + dx, leader.map_y + dy

        if not (1 <= to_x <= self.width) or not (1 <= to_y <= self.height):
            self._settle()
            return

        if self.solid[to_y - 1][to_x - 1]:
            self._settle()
            return

        for i in reversed(order):
            if i <= first or characters[i].dead:
                continue

            j = self._next_alive_ahead(order, i)

            if j is None:
                continue

            characters[i].map_x = characters[j].map_x
            characters[i].map_y = characters[j].map_y

        leader.map_x, leader.map_y = to_x, to_y

        self.moving = True
        last_tween = None

        for character in characters.values():
            if character.dead:
                continue

            target_x = (character.map_x - 1) * settings.TILE_SIZE
            target_y = (
                character.map_y - 1
            ) * settings.TILE_SIZE - character.height / 2
            last_tween = Timer.tween(
                0.3, [(character, {"x": target_x, "y": target_y})]
            )

        if last_tween is not None:
            last_tween.finish(lambda: self._on_step_finished(to_x, to_y))

    def _settle(self) -> None:
        for character in self.party.characters.values():
            if not character.dead:
                character.change_state("idle")

    def _on_step_finished(self, x: int, y: int) -> None:
        self.moving = False

        if (x, y) == (self.door["x"], self.door["y"]):
            self._settle()
            self._exit_hall()
            return

        if self.held["move_left"]:
            self._attempt_move("left")
        elif self.held["move_right"]:
            self._attempt_move("right")
        elif self.held["move_up"]:
            self._attempt_move("up")
        elif self.held["move_down"]:
            self._attempt_move("down")
        else:
            self._settle()

    def _exit_hall(self) -> None:
        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState

        def on_fade_in_complete() -> None:
            self.state_machine.pop()  # GuildHallState (runs exit(), which calls on_exit)
            self.state_machine.push(
                FadeOutState(self.state_machine),
                color=(255, 255, 255),
                time=1,
                on_complete=lambda: None,
            )

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(255, 255, 255),
            time=1,
            on_complete=on_fade_in_complete,
        )

    def _near_any_bed(self, character: Any) -> bool:
        """Same adjacency rule World._try_interact uses for NPCs (within 1
        tile, diagonals included), checked against every cell a bed
        occupies rather than just its top-left corner."""
        for bed in self.bed_positions:
            for cell_x in (bed["x"], bed["x"] + 1):
                for cell_y in (bed["y"], bed["y"] + 1):
                    if (
                        abs(cell_x - character.map_x) <= 1
                        and abs(cell_y - character.map_y) <= 1
                    ):
                        return True

        return False

    def _try_interact(self) -> None:
        leader = self.party.first_alive()

        if leader is not None and self._near_any_bed(leader):
            self._rest_at_inn()

    def _rest_at_inn(self) -> None:
        from src.states.game.DialogueState import DialogueState

        for character in self.party.characters.values():
            character.dead = False
            character.current_hp = character.hp

        self._place_party()
        settings.SOUNDS["powerup"].play()

        self.state_machine.push(
            DialogueState(self.state_machine),
            text="The party has been fully rested",
        )

    def update(self, dt: float) -> None:
        for character in self.party.characters.values():
            if not character.dead:
                character.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in self.held:
            if input_data.pressed:
                self.held[input_id] = True

                if not self.moving:
                    self._attempt_move(input_id.split("_")[1])
            elif input_data.released:
                self.held[input_id] = False
        elif input_id == "space" and input_data.pressed:
            self._try_interact()

    def render(self, surface: pygame.Surface) -> None:
        # The room is smaller than the screen (same BATTLE_PADDLE framing
        # as BattleState), so the margins around it are filled solid
        # first -- otherwise whatever's under this state in the stack
        # (the town) would still show through them.
        surface.fill((0, 0, 0))

        room = surface.subsurface(
            pygame.Rect(
                BATTLE_PADDLE["x"] * settings.TILE_SIZE,
                BATTLE_PADDLE["y"] * settings.TILE_SIZE,
                self.width * settings.TILE_SIZE,
                self.height * settings.TILE_SIZE,
            )
        )
        self.tilemap.render(room)

        for character in self.party.characters.values():
            character.render(room)
