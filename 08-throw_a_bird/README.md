# 08 - Throw a Bird

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is a physics-based artillery game in the style of Angry Birds, ported from a Defold project onto Python with `pygame-ce`, the gale-engine, and its Box2D-backed physics module.

## Requirements and running it

You need Python 3 and two dependencies:

```bash
pip install pygame-ce gale-engine
```

It has been tested with Python 3.14, `pygame-ce` 2.5.8 and `gale-engine` 1.16.0. To start, from this directory:

```bash
python main.py
```

## Controls

| Input | Action |
|---|---|
| Drag near the bird | Aim (release to fling it) |
| Drag anywhere else | Pan the camera |
| Space | Split the bird mid-flight |
| Esc | Quit |

## The game

One bird sits loaded on a slingshot at a time. Drag it back and let go to fling it at a tower of stone and wood blocks holding two kinds of aliens. The camera follows the bird and zooms out the farther it travels, and a wind zone waits past each edge of the level to nudge anything that drifts too far back toward the play area.

Stone and wood blocks take damage from hard enough impacts, showing a cracked look before they finally break; wood also scatters a few chips when it goes. Every fresh bird has a fifty-fifty chance of coming out blue instead of the plain red one. Knock down enough of the tower to destroy every alien and you win. Click anywhere on the victory screen to try again.

## Work in this submission

### Splitting the bird into three

Only the blue bird carries this ability. Pressing space while it is in flight splits it into three: the original keeps flying on its own unchanged trajectory, and two new birds spawn alongside it, their velocity rotated 20 degrees off the original's, one up and one down, at the same speed it had at the moment of the split (`PlayState._split_bird`).

The two new birds start a short distance from the original along their own heading rather than right on top of it. `gale.physics.Body.touching_bodies` treats any overlap as a collision, so three birds created on the exact same point would read as having already hit each other before the throw ever continued.

### Collision disables the split

Each bird tracks its own `has_collided` flag (`src/entity/Bird.py`), checked every physics step against whatever it is currently touching. The instant it registers a real hit, ground or block, its sprite switches to a hurt look and the split ability turns off for that bird for the rest of the throw. Wind zones are excluded from this check: they are invisible boundary triggers, not something the bird actually hit, even though `touching_bodies` reports overlapping them too.

### The throw doesn't end until every bird settles

`PlayState` now tracks every bird currently in the air as `self.birds`, not just the one that started the throw. A fresh bird only loads onto the slingshot once every bird in that list, the original and any it split into, has slowed down close to a stop; while even one of them is still moving, the throw stays open.

## Code layout

Files changed for this submission:

- `src/entity/Bird.py`: now builds from `BIRDS["red"]` or `BIRDS["blue"]`, tracks `has_collided` and `powerup_activated`, and switches to its hurt sprite once it has taken a hit.
- `src/definitions/entity.py`: `BIRDS`, a red and a blue entry (blue lighter and a touch smaller), each naming both its normal and hurt sprite.
- `src/states/game/PlayState.py`: `self.bird` (single) became `self.birds` (a list), plus `_spawn_bird` (rolls the color, rebuilds the bird, clears out every bird from the last throw) and `_split_bird`.
- `settings.py`: the two hurt bird textures, and the space key bound to the split action.

Everything else keeps the structure the project already had: `src/world/Level.py`, `Destructible.py`, `Debris.py` and `Background.py` for the tower, the ground, and the wind zones, and `VictoryState` for the win screen.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
