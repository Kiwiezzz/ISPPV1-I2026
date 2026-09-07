"""
This file contains BossWalkState: the same erratic wander the other
enemies use (EntityWalkState), except the fire golem has a single "idle"
clip that reads fine facing any way, so there are no directional
animation swaps. It is its own class -- rather than the boss reusing
EntityWalkState directly -- so the fireball attack can be layered on here
later without touching the shared enemy state.
"""

import random

from src.states.entity.EntityWalkState import (
    _DIRECTIONS,
    _MOVE_COMMANDS,
    _STOP_COMMANDS,
    EntityWalkState,
)


class BossWalkState(EntityWalkState):
    def enter(self) -> None:
        self.entity.change_animation("idle")

        # AI wander bookkeeping (same fields EntityWalkState.enter sets).
        self.move_duration = 0
        self.movement_timer = 0
        self.bumped = False

    def _pick_direction(self) -> None:
        for stop in _STOP_COMMANDS:
            stop.execute(self.entity)

        direction = random.choice(_DIRECTIONS)
        _MOVE_COMMANDS[direction].execute(self.entity)
