"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TakeTurnState: the battle's ATB scheduler.
On enter, every living combatant (party + enemies) starts resting. Each
one calls back the instant its own speed_time elapses (BattleEntity.
start_resting, driven by gale.timer.Timer, keeps ticking regardless of
what is pushed on top of this state); whoever calls back first is queued
and, once nothing else is mid-turn, gets to act -- a character through
SelectActionState, an enemy through AI picking one of its own actions
against a random living target. After acting, an entity rests again
using its own speed_time, and the next queued entity goes. Also handles
the victory (EXP/level-up) and defeat (game over) end-of-battle flows.
"""

import math
import random
from typing import Any, Dict, List, Optional

from gale.state import BaseState
from gale.timer import Timer

import settings
from src.entity.Character import Character


class TakeTurnState(BaseState):
    def enter(self, battle_state: Any) -> None:
        self.battle_state = battle_state
        self.battle_state.battle_over = False
        self.ready_queue: List[Any] = []
        self.acting: Optional[Any] = None
        self.enemy_attacks_in_a_row = 0
        self._victory_channel = None

        for character in self.battle_state.party.characters.values():
            if not character.dead:
                character.start_resting(
                    on_ready=self._on_entity_ready, delay=self._initial_delay(character)
                )

        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.start_resting(
                    on_ready=self._on_entity_ready, delay=self._initial_delay(enemy)
                )

    def _initial_delay(self, entity: Any) -> float:
        spread = random.uniform(-0.4, 0.4)
        return max(0.1, entity.speed_time + spread)

    def _party_keys(self):
        return sorted(self.battle_state.party.characters.keys())

    # -- scheduling -------------------------------------------------------

    def _on_entity_ready(self, entity: Any) -> None:
        if self.battle_state.battle_over or entity.dead:
            return

        self.ready_queue.append(entity)

        if self.acting is None:
            self._start_next_turn()

    def _start_next_turn(self) -> None:
        while self.ready_queue:
            entity = self.ready_queue.pop(0)

            if entity.dead:
                continue

            self.acting = entity

            if isinstance(entity, Character):
                self._start_character_turn(entity)
            else:
                self._resolve_enemy_action(entity)
            return

    def _finish_turn(self, entity: Any) -> None:
        self.acting = None

        if self.battle_state.battle_over:
            return

        if not entity.dead:
            entity.start_resting(on_ready=self._on_entity_ready)

        self._start_next_turn()

    # -- party turns ---------------------------------------------------

    def _start_character_turn(self, character: Any) -> None:
        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"Turn for {character.name}! Select an action.",
            on_close=lambda: self._prompt_action(character),
        )

    def _prompt_action(self, character: Any) -> None:
        from src.states.game.SelectActionState import SelectActionState

        def on_action_selected(action: Optional[Dict[str, Any]]) -> None:
            if all(enemy.dead for enemy in self.battle_state.enemies):
                self.battle_state.battle_over = True
                self._victory()
                return

            self._finish_turn(character)

        self.state_machine.push(
            SelectActionState(self.state_machine),
            battle_state=self.battle_state,
            entity=character,
            on_action_selected=on_action_selected,
        )

    # -- enemy turns ----------------------------------------------------

    def _resolve_enemy_action(self, enemy: Any) -> None:
        self.enemy_attacks_in_a_row += 1
        action = random.choice(enemy.actions)

        if action["target_type"] == "enemy":
            targets = list(self.battle_state.party.characters.values())
            target_label = "you"
        else:
            targets = self.battle_state.enemies
            target_label = "them"

        if action["require_target"]:
            alive = [target for target in targets if not target.dead]
            target = random.choice(alive)
            amount = action["func"](enemy, target, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()
            Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])
            message = f"{enemy.name} used {action['name']} for {amount} HP on {target.name}."
        else:
            alive_targets = [target for target in targets if not target.dead]
            amount = action["func"](enemy, alive_targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()

            for target in alive_targets:
                Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])

            message = (
                f"{enemy.name} used {action['name']} for {amount} HP on all of "
                f"{target_label}."
            )

        if all(character.dead for character in self.battle_state.party.characters.values()):
            self.battle_state.battle_over = True
            self._faint()
            return

        from src.states.game.BattleMessageState import BattleMessageState

        def on_message_close() -> None:
            if (
                self.enemy_attacks_in_a_row < 3
                and enemy.klass == "boss"
                and random.randint(1, 3) == 1
            ):
                self._resolve_enemy_action(enemy)
            else:
                self.enemy_attacks_in_a_row = 0
                self._finish_turn(enemy)

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=message,
            on_close=on_message_close,
        )

    # -- victory / experience --------------------------------------------

    def _victory(self) -> None:
        settings.stop_music("battle")
        self._victory_channel = settings.SOUNDS["victory"].play(loops=-1)

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message="Victory!",
            on_close=self._start_exp,
        )

    def _start_exp(self) -> None:
        total_level = sum(enemy.level for enemy in self.battle_state.enemies)
        num_characters = len(self.battle_state.party.characters)
        opponent_level = total_level / num_characters
        self._inc_exp(0, opponent_level)

    def _inc_exp(self, index: int, opponent_level: float) -> None:
        keys = self._party_keys()

        if index >= len(keys):
            self._fade_out()
            return

        character = self.battle_state.party.characters[keys[index]]

        if character.dead:
            self._inc_exp(index + 1, opponent_level)
            return

        exp = math.ceil(
            (character.hpiv + character.attackiv + character.defenseiv + character.magiciv)
            * opponent_level
        )

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"{character.name} earned {exp} experience points!",
            on_close=None,
            can_input=False,
        )
        Timer.after(1.5, lambda: self._apply_exp(character, exp, index, opponent_level))

    def _apply_exp(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        settings.SOUNDS["exp"].play()
        new_value = min(character.current_exp + exp, character.exp_to_level)
        Timer.tween(
            0.5,
            [(character.exp_bar, {"value": new_value})],
            on_finish=lambda: self._exp_applied(character, exp, index, opponent_level),
        )

    def _exp_applied(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        # Pops the can_input=False experience-gain message, which never
        # auto-closes on its own.
        self.state_machine.pop()
        character.current_exp += exp

        if character.current_exp >= character.exp_to_level:
            settings.SOUNDS["levelup"].play()
            character.current_exp -= character.exp_to_level
            last_level = character.level
            increases = character.level_up()
            hp_increase = increases[0]
            Timer.tween(
                0.5, [(character.energy_bar, {"value": character.current_hp - hp_increase})]
            )

            from src.states.game.BattleMessageState import BattleMessageState

            message = (
                f"Congratulations! {character.name} advanced from level "
                f"{last_level} level {character.level}!"
            )
            self.state_machine.push(
                BattleMessageState(self.state_machine),
                battle_state=self.battle_state,
                message=message,
                on_close=lambda: self._show_stats(character, increases, index, opponent_level),
            )
        else:
            self._inc_exp(index + 1, opponent_level)

    def _show_stats(self, character: Any, increases: Any, index: int, opponent_level: float) -> None:
        from src.states.game.StatsMenuState import StatsMenuState

        self.state_machine.push(
            StatsMenuState(self.state_machine),
            character=character,
            stats=increases,
            on_close=lambda: self._inc_exp(index + 1, opponent_level),
        )

    def _fade_out(self) -> None:
        if self._victory_channel is not None:
            self._victory_channel.stop()

        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState

        if self.battle_state.final_boss:

            def on_complete() -> None:
                # Pops this lingering TakeTurnState, then the BattleState
                # underneath it (matches the original's "pop twice"). The
                # second pop runs BattleState.exit(), which always calls
                # the on_exit it was pushed with (see
                # PartyWalkState._trigger_encounter) -- for a NORMAL battle
                # that's the whole point (it un-pauses the overworld's
                # "world"/"town" music the encounter had merely paused,
                # not stopped, so walking around resumes right where the
                # music left off), but here there's no overworld to return
                # to: the very next thing on screen is TheEndState. Without
                # silencing what that on_exit just resumed, it played
                # underneath "the-end" for the rest of the game -- the two
                # overlapping tracks this whole fix is about. _victory
                # already stopped "battle" and _fade_out already stopped
                # the "victory" jingle, so this only has the resumed
                # overworld music left to clean up, but stopping "battle"
                # again too is harmless and keeps this correct even if
                # that ordering ever changes.
                self.state_machine.pop()
                self.state_machine.pop()
                settings.stop_music("battle")
                settings.stop_music("world")
                settings.stop_music("town")
                # A bare SOUNDS["the-end"].play() (the original code here)
                # starts a plain, untracked Sound channel -- unlike every
                # other music cue in this game, it was never routed
                # through play_music, so nothing could stop it the same
                # way the stops above stop everything else (see
                # TheEndState's restart handler).
                settings.play_music("the-end")

                from src.states.game.TheEndState import TheEndState

                self.state_machine.push(TheEndState(self.state_machine))
                self.state_machine.push(
                    FadeOutState(self.state_machine),
                    color=(0, 0, 0),
                    time=1,
                    on_complete=lambda: None,
                )

            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(0, 0, 0),
                time=3,
                on_complete=on_complete,
            )
        else:

            def on_complete() -> None:
                # Pops this lingering TakeTurnState, then the BattleState
                # underneath it (BattleState.exit() stops battle music and
                # restores the party's overworld position/music).
                self.state_machine.pop()
                self.state_machine.pop()
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
                on_complete=on_complete,
            )

    def _faint(self) -> None:
        settings.stop_music("battle")
        settings.SOUNDS["game-over"].play()

        from src.states.game.FadeInState import FadeInState

        def on_complete() -> None:
            from src.states.game.GameOverState import GameOverState

            self.state_machine.push(GameOverState(self.state_machine))

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(0, 0, 0),
            time=1,
            on_complete=on_complete,
        )

    def update(self, dt: float) -> None:
        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.update(dt)
