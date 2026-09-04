
from gale.timer import Timer

from src.states.entities.BaseEntityState import BaseEntityState


class SnailHiddenState(BaseEntityState):
    # Seconds the snail stays hidden before re-emerging
    HIDE_DURATION: float = 3.0

    def enter(self) -> None:
        self.entity.change_animation("hidden")
        self.entity.vx = 0

        # After HIDE_DURATION seconds, return to walking in the same direction
        Timer.after(
            self.HIDE_DURATION,
            lambda: self.entity.change_state("walk", self.entity.flipped),
        )

    def update(self, dt: float) -> None:
        # The snail is stationary while hidden; nothing to update each frame
        pass