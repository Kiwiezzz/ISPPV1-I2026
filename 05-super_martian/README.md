# 05 - Super Martian

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is a Super Mario style side-scrolling platformer, written in Python on top of `pygame-ce` and the Gale engine.

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
| Arrows or A / D | Move left and right |
| Space or left mouse button | Jump |
| P | Pause |
| Enter | Confirm (menus) |
| Esc | Quit |

The jump has variable height: tap for a short hop, hold to reach the full arc.

## The game

You run and jump through two levels collecting coins before the timer runs out. Coins are worth 1, 5, 20 or 50 points depending on their colour, and they respawn a few seconds after you pick them up. Each level has a countdown that starts at 150 seconds; if it hits zero, or you fall off the bottom of the map, you die.

Two kinds of creatures get in the way: snails that walk along the ground and creatures that fly across the level from one side to the other. Jumping on a flying creature knocks it out of the air and gives you 50 points. Jumping on a snail makes it hide in its shell for a few seconds instead of dying, and while it is hidden or falling it can no longer hurt you. Running into a creature any other way kills you.

## Work in this submission

### New level (Tiled)

Level 2 is a new level built in Tiled (`assets/tilemaps/level2.json`, 50 by 12 tiles). It has its own layout, its own set of coins and snails, and the key block described below. It draws from `tileset.png` for the terrain and from `tileset2.png` for the hit block. Level 1 was also rebuilt with `tileset2.png`. Flying creatures spawn on both levels at random intervals.

### Key block and key

Level 2 contains one special tile marked in Tiled with the `is_key` property, placed two columns right and three rows up from where the player starts. It behaves as a fully solid block: you cannot pass through it, and hitting it from below with your head triggers it.

The check lives in `GameEntity.update`: when the entity is moving up and bumps into a tile overhead, it reads the tile above its head and, if that tile has `is_key`, calls `on_hit_key_block`. `Player` overrides that method. `PlayState` finds the block when the level loads, remembers its position and tile id, and then hides it by clearing the cell, so the block only shows up once the score target is reached.

When you hit the revealed block, `Player.on_hit_key_block` plays the question-block sound and creates a `Key` at the block's position. The key starts fully hidden inside the block and rises 16 pixels over half a second with an `out_cubic` tween. Its `render` method uses a stencil so only the part that has already come out of the block is drawn, which sells the idea that the key is growing out of it. The key is not collectible until the tween finishes.

Picking up the key ends the level.

### Score target and victory

`settings.KEY_SCORE_TARGET` is 450. The HUD shows your progress as `Score: X/450`.

When you reach the target the key block appears, the countdown timer stops, coins stop counting, and creatures can no longer hurt you. You can still move, so you walk over to the block, jump up to hit it, and collect the key that comes out.

Collecting the key plays the victory sound, freezes the player, and fades the screen to black over 3.5 seconds before loading the next level, or the end screen after level 2. Entering a level runs the same overlay in reverse, fading from black over half a second.

### Snail shell state

`SnailHiddenState` is the state a snail enters after being stomped. It stops the snail, switches it to the shell animation, and after three seconds sends it back to walking in the same direction it was facing.

## Code layout

Files added or changed for this submission:

- `assets/tilemaps/level2.json`: the new level, including the key block.
- `assets/tilemaps/level1.json`, `assets/graphics/tileset2.png`: level 1 rebuilt with the new tileset.
- `assets/graphics/key.png`, `assets/sounds/hit_block.wav`, `hit_question_block.wav`, `victory.wav`: the key sprite and the new sound effects.
- `src/Key.py`: the key item, its emergence tween and the stencil rendering.
- `src/states/entities/creatures_states/SnailHidden.py`: the snail shell state.
- `src/GameEntity.py`: the overhead `is_key` tile check and the `on_hit_key_block` hook.
- `src/Player.py`: `on_hit_key_block`, which spawns the key.
- `src/states/game_states/PlayState.py`: hiding and revealing the key block, the score and victory logic, the stomp handling, and the fade transitions.
- `src/definitions/creatures.py`: the `hidden` state and animation for both snail types.
- `settings.py`: the new textures, sounds, `NUM_LEVELS`, `KEY_SCORE_TARGET` and window size.

Everything else keeps the structure of the original study case: `src/states/` for the game and entity state machines, `src/mixins/` for the drawable, animated and collidable behaviour shared by entities, `GameEntity.py` and `Player.py` for movement and collisions, and `GameLevel.py` for loading a Tiled map and its creatures and coins.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
