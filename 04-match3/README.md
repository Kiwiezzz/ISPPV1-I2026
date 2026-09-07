# 04 - Match 3

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is a Bejeweled style match-3 puzzle, written in Python on top of `pygame-ce` and the Gale engine.

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

The whole game is played with the mouse. Press on a tile, drag it onto a neighbour, and release to make the move. Click a power-up to detonate it in place. `Esc` quits, `Enter` confirms on the menus.

## The game

The board is 8 by 8. You swap adjacent tiles to line up three or more of the same colour; those tiles clear, the ones above fall down, and new tiles drop in from the top. Chains keep scoring until the board settles. Each level gives you 260 seconds and a score goal (`level * 1.25 * 1000 * 1.5`); reach it to move on, run out of time and it is game over. Later levels use more tile colours, so matches are harder to spot.

## Work in this submission

### Drag and drop

Tiles are moved by dragging instead of clicking twice. When you press the mouse on a tile it becomes the dragged tile and its starting cell and pixel position are saved. While the button is held, `PlayState.update` sets the tile's position to the mouse position every frame (the raw mouse coordinates are scaled from the window size down to the virtual resolution first), so the tile follows the cursor.

On release, `PlayState.on_input` looks at where you let go:

- Same cell, and the tile is a power-up: it activates.
- An adjacent cell: the swap is attempted.
- Anywhere else: the tile tweens back to where it started.

### Only match-forming moves are allowed

When you drop a tile on a neighbour, the two tiles are swapped in the board and `Board.calculate_matches_for` runs in `simulate=True` mode. If it finds no match the swap is undone and the tile slides back to its cell. A move only goes through if it creates at least one match.

### Automatic board reshuffle

`Board._initialize_tiles` already rejects a starting board with no possible matches and builds another. The submission extends this to mid-game: `Board.has_possible_matches` tries every horizontal and vertical swap on the current board and reports whether any of them would match (it also returns true if a power-up is sitting on the board, since you can always click that). After a move settles with nothing left to clear, `PlayState._calculate_matches` calls that check and, while it fails, rebuilds the board until a playable one comes up.

### Power-ups

Both power-ups are `Tile` subclasses, so they fall, can be dragged and swapped like any tile, and can be caught in a later match. They live in `src/powerups/`. `Board.calculate_matches_for` creates one when a match contains a straight run (rows and columns are measured separately, so an L-shape of five does not count as a five-match):

**Line bomb**, from a run of exactly 4. It spawns on the moved tile's cell and keeps that tile's colour. When it goes off, by a direct click or by being part of a match, it clears every tile in its row and its column.

**Colour bomb**, from a run of 5 or more. Same spawn rule and colour rule. When it goes off it clears every tile of that colour anywhere on the board.

`Board.remove_matches` walks the list of tiles being destroyed and, whenever it hits a bomb, adds that bomb's targets to the list. A bomb caught in another bomb's blast explodes too, so chains carry through. Destroyed tiles are worth 50 points each, including the ones added by a chain reaction.

## Code layout

Files added or changed for this submission:

- `src/powerups/LineBomb.py`, `src/powerups/ColorBomb.py`, `src/powerups/__init__.py`: the two power-up tiles and their explosion targets.
- `src/Board.py`: power-up generation, `has_possible_matches`, the reshuffle loop, chain-reaction handling in `remove_matches`, and per-level colour scaling.
- `src/states/PlayState.py`: the drag-and-drop input, the simulated-swap move check, the reshuffle call, and power-up activation.
- `src/states/BeginGameState.py`: passes the level through to the board so it can scale its colours.
- `assets/graphics/line_bomb.png`, `assets/graphics/Color_bomb.png`, `assets/sounds/bomb.wav`: the power-up overlays and the explosion sound.
- `settings.py`: the new textures and sound.

Everything else keeps the structure of the original study case: `src/Match3.py` for the main loop and the state machine, `src/states/` for the menu, begin, play and game-over states, `src/Board.py` and `src/Tile.py` for the grid and the tiles.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
