# 06 - The Legend of the Princess

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is a 16-bit style dungeon ARPG, written in Python on top of `pygame-ce` and the gale-engine.

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

| Key | Action |
|---|---|
| Arrows or WASD | Move |
| Space | Sword |
| E | Shoot an arrow (once you have the bow) |
| Enter | Interact (open the chest) |
| Esc | Quit |

## The game

You start in a dungeon whose rooms are generated as you cross each doorway, with a camera transition between them. Enemies wander around and hurt you on contact (skeletons, slimes, bats, ghosts and spiders), and you can pick up and throw the pots on the floor.

At some point the chest room shows up. Opening the chest gives you the bow, and from then on you can shoot arrows as well as use the sword. Once you have the bow, crossing a doorway may take you to the boss room.

## Work in this submission

### Chest and bow system

The chest is generated once, at random, in its own room (`ChestRoom`). It opens when the player stands right below it, facing up, and presses Enter. A short animation then plays where the character lifts the bow, reusing the `pot-lift` state that already existed for the pots.

Shooting is built with the Factory pattern, as the assignment required:

- `Arrow` is a `GameObject` that represents the arrow. Its internal state (`left`, `right`, `up`, `down`) picks the texture already rotated in `settings.py`.
- `Bow` holds a `Factory(Arrow)` and exposes `fire(x, y, direction)`, which creates the arrow with the factory and returns a `Projectile` ready to add to the room.
- The player keeps a `Bow` instance in `self.bow`. The `PlayerBowState` state works out the spawn point from the direction and calls `self.entity.bow.fire(...)`.

While the player has the bow equipped, the walk and idle animations use the character sheet with the bow in hand. Swinging the sword or picking up a pot puts it away again.

### Room and boss

The boss room (`BossRoom`) has no enemies, pots or switches, and only keeps the doorway you came in through. The other three sides stay solid wall. The boss appears on the side opposite that doorway. When you enter, the door closes, and it opens again when the boss dies.

The boss is a fire golem. Its behaviour:

- It moves erratically and a bit faster than the player, using the same AI logic as the other enemies (`BossWalkState`, `BossIdleState`).
- Every few seconds it throws a fireball (`Fireball`) at the spot where the player was standing at that moment. The fireball travels in a straight line and does not chase you. If it reaches you, you die.
- Touching its body costs a full heart.
- It is immune to the sword. In its normal state only arrows hurt it.
- When an arrow hits it, it spends five seconds in a vulnerable state: it switches to the inverted colour palette, and during that window the sword does hurt it. In the last second or so it flickers between the inverted and the normal look before going back to normal. While vulnerable it stays still and does not shoot.

## Code layout

Files I added or changed for this submission:

- `src/Arrow.py`, `src/Bow.py`: the arrow and the bow with the factory.
- `src/Fireball.py`: the boss projectile.
- `src/states/entity/BossWalkState.py`, `BossIdleState.py`, `BossInvertedState.py`: the boss states.
- `src/states/entity/player/PlayerBowState.py`: the player's shooting state.
- `src/world/BossRoom.py`: the boss room and the handling of its fireballs.
- `src/world/ChestRoom.py`, `Dungeon.py`, `Room.py`, `Player.py`, `settings.py` and `definitions/entity.py`: changes to wire all of the above together.

Everything else keeps the structure of the original study case: `src/world/` for the map and the rooms, `src/states/` for the game and entity state machines, and `Entity.py` with `Player.py` for movement, collisions, animation and health.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
