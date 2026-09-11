from typing import Any

import pygame

from gale.state import BaseState
from gale.text import render_text

import settings
from src.definitions.entity import ENTITY_HEIGHT, ENTITY_WIDTH
from src.gui.Panel import Panel

_MARGIN = 4
_FADED_ALPHA = 90
_WHITE = (255, 255, 255)
_SPRITE_SCALE = 2
_DEAD_FILL = (110, 30, 30)
_ALIVE_FILL = (56, 56, 56)


class PartyStatus(BaseState):
    def enter(self, play_state: Any) -> None:
        self.play_state = play_state
        self.party = play_state.world.party
        self.font = settings.FONTS["small"]

        panel_w = (settings.VIRTUAL_WIDTH - 3 * _MARGIN) / 2
        panel_h = (settings.VIRTUAL_HEIGHT - 3 * _MARGIN) / 2
        self._panel_slots = [
            (_MARGIN, _MARGIN),
            (_MARGIN * 2 + panel_w, _MARGIN),
            (_MARGIN, _MARGIN * 2 + panel_h),
            (_MARGIN * 2 + panel_w, _MARGIN * 2 + panel_h),
        ]
        self._panel_size = (panel_w, panel_h)

    def close(self) -> None:
        self.state_machine.pop()

    # -- BaseState -------------------------------------------------------

    def update(self, dt: float) -> None:
        pass

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_data.pressed and input_id in ("enter", "party_menu", "space"):
            self.close()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel_w, panel_h = self._panel_size

        for slot, (px, py) in zip(sorted(self.party.characters.keys()), self._panel_slots):
            character = self.party.characters[slot]
            fill_color = _DEAD_FILL if character.dead else _ALIVE_FILL
            Panel(px, py, panel_w, panel_h).render(surface, fill_color=fill_color)
            self._render_member(surface, character, px, py)

        render_text(
            surface,
            "Enter to close",
            self.font,
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT - 9,
            _WHITE,
            center=True,
        )

    def _render_member(
        self, surface: pygame.Surface, character: Any, px: float, py: float
    ) -> None:
        self._render_sprite(surface, character, px + 6, py + 6)

        x = px + 12 + ENTITY_WIDTH * _SPRITE_SCALE
        y = py + 5
        line = 10

        header = f"{character.name} ({character.klass})"
        if character.dead:
            header += "  DOWN"
        render_text(surface, header, self.font, x, y, _WHITE)

        stats = [
            f"Lv {character.level}",
            f"HP {int(character.current_hp)}/{int(character.hp)}",
            f"XP {int(character.current_exp)}/{int(character.exp_to_level)}",
            f"ATK {int(character.attack)}  DEF {int(character.defense)}  MAG {int(character.magic)}",
        ]
        for i, text in enumerate(stats, start=1):
            render_text(surface, text, self.font, x, y + i * line, _WHITE)

        actions_y = y + (len(stats) + 1) * line + 2
        render_text(surface, "Actions:", self.font, x, actions_y, _WHITE)

        for i, action in enumerate(character.actions, start=1):
            is_heal = action["target_type"] == "character"
            alpha = 255 if is_heal else _FADED_ALPHA
            self._faded_text(surface, action["name"], x + 8, actions_y + i * line, alpha)

    def _render_sprite(
        self, surface: pygame.Surface, character: Any, x: float, y: float
    ) -> None:
        if character.current_animation is None:
            return

        frame = settings.TEXTURES[character.texture].subsurface(
            character.current_animation.get_current_frame()
        )
        frame = pygame.transform.scale(
            frame, (ENTITY_WIDTH * _SPRITE_SCALE, ENTITY_HEIGHT * _SPRITE_SCALE)
        )
        surface.blit(frame, (x, y))

    def _faded_text(
        self, surface: pygame.Surface, text: str, x: float, y: float, alpha: int
    ) -> None:
        text_surface = self.font.render(text, True, _WHITE)
        text_surface.set_alpha(alpha)
        surface.blit(text_surface, (x, y))
