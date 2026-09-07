"""
This file contains BossIdleState: the short pause between wander bursts,
same timing as EntityIdleState, but pinned to the golem's single "idle"
clip. Kept as its own class so boss-only logic can be added here later.
"""

from src.states.entity.EntityIdleState import EntityIdleState


class BossIdleState(EntityIdleState):
    def enter(self) -> None:
        self.entity.change_animation("idle")

        # AI wait bookkeeping (same fields EntityIdleState.enter sets).
        self.wait_duration = 0
        self.wait_timer = 0
