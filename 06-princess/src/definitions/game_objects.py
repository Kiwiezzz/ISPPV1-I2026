"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for game objects.
"""

from typing import Any, Dict

import settings


def _pickup_heart(player, obj) -> None:
    player.heal(2)
    settings.SOUNDS["heart-taken"].play()


GAME_OBJECT_DEFS: Dict[str, Dict[str, Any]] = {
    "switch": {
        "type": "switch",
        "texture": "switches",
        "frame": 2,
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "unpressed",
        "states": {
            "unpressed": {"frame": 2},
            "pressed": {"frame": 1},
        },
    },
    "pot": {
        "type": "pot",
        "texture": "tiles",
        "frame": 16,
        "width": 16,
        "height": 16,
        "solid": True,
        "consumable": False,
        "default_state": "default",
        "takeable": True,
        "states": {
            "default": {"frame": 16},
        },
    },
    # Definition of heart as a consumable object type.
    "heart": {
        "type": "heart",
        "texture": "hearts",
        "frame": 5,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": True,
        "default_state": "default",
        "states": {
            "default": {"frame": 5},
        },
        "on_consume": _pickup_heart,
    },
    "chest": {
        "type": "chest",
        "texture": "chest-closed",
        "frame": 1,
        "width": 32,
        "height": 16,
        "solid": True,
        "consumable": False,
        "default_state": "closed",
        "states": {
            "closed": {"texture": "chest-closed", "frame": 1},
            "opened": {"texture": "chest-open", "frame": 1},
        },
    },
    "arrow": {
        "type": "arrow",
        "texture": "arrow-left",
        "frame": 1,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": False,
        "default_state": "left",
        "states": {
            "left": {"texture": "arrow-left", "frame": 1},
            "right": {"texture": "arrow-right", "frame": 1},
            "up": {"texture": "arrow-up", "frame": 1},
            "down": {"texture": "arrow-down", "frame": 1},
        },
    },
}
