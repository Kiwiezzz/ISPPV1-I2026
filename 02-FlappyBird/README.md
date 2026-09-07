# 02 - Flappy Bird

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is a Flappy Bird clone, written in Python on top of `pygame-ce` and the Gale engine.

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
| Left mouse button | Flap |
| A / D | Move the bird left and right (hard mode only) |
| Esc | Pause and resume |
| W / S or Up / Down | Move through a menu |
| Enter | Confirm |

## The game

Flap to keep the bird in the air and fly through the gaps between the log pairs without touching them or the ground. Each pair you clear is worth one point. From the title screen you pick Normal or Hard mode before the countdown starts.

## Work in this submission

### Pause state

`PauseState` is toggled with `Esc`. `PlayingState` reacts to that key by switching to the pause state and handing over the current `world`, `bird`, `score` and `game_mode`; `PauseState` reacts to the same key by handing them straight back to `PlayingState`. Because the world and the bird are passed through the state change rather than rebuilt, `PlayingState.enter` reuses them and the game continues from exactly where it stopped.

The pause screen also has a small menu, Continue / Restart / Exit, moved with `W`/`S` or the arrows and chosen with `Enter`. Restart and Exit clean up the ghost power-up if it happened to be active (bird opacity back to full, background music restored).

The assignment asks which state methods this needs:

- `enter`: yes. It receives the game objects to hold and sets up the menu.
- `render`: yes. It draws the frozen world and bird, a dark overlay, the "Paused" label and the menu.
- `on_input` (`handle_input`): yes. It toggles back to play, moves the menu selection and acts on the choice.
- `update`: no. Nothing moves while paused, so there is nothing to advance per frame.
- `exit`: no. There is no state to tear down on the way out; everything the next state needs was passed in through `enter`.

### Game modes (Strategy pattern)

`GameMode` is an abstract base with `update`, `is_game_over`, `reset`, `on_score`, `render` and `on_input`. `PlayingState` holds one `GameMode` and delegates each of those calls to it, so it does not know or care which mode is running. The title screen builds a `NormalMode` or a `HardMode` and passes it down through the countdown into play.

**Normal mode** keeps the original behaviour. Log pairs spawn on a fixed 1.5-second timer, each one drifting a little from the height of the last, built through a `Factory(LogPair)`. A flap is the only input.

**Hard mode** adds:

- **Horizontal movement.** `A` and `D` set the bird's horizontal velocity, so you can move across the screen as well as up and down.
- **Uneven obstacles.** The spawn interval is random (between about 1.2 and 2.5 seconds), and so is the vertical gap of each pair. How far a pair's height can move from the previous one is tied to how long since the last spawn (`(interval - 1.0) * 80`), and the result is clamped so a gap is always reachable from the one before it.
- **Opening and closing logs.** Around 60% of pairs are a `MovingLogPair`, whose gap oscillates with a sine wave. When the gap nearly closes it plays a snapping sound once.
- **Ghost power-up.** Created with a `Factory(PowerUp)` at a random height and scrolling in from the right. Picking it up removes it from the scene, turns the bird semi-transparent, plays a sound, and swaps the music for the ghost track. For 6 seconds the bird passes through the logs (the floor still kills you), with the last 2 seconds flickering as a warning. When it runs out the bird's opacity and the music return to normal.

`HardMode.is_game_over` reflects this: the ground is always fatal, and while the ghost is active log collisions are ignored.

## Code layout

Files added or changed for this submission:

- `src/states/PauseState.py`: the pause screen and its menu.
- `src/states/gamemode/GameMode.py`, `NormalMode.py`, `HardMode.py`, `__init__.py`: the Strategy base and the two modes.
- `src/MovingLogPair.py`: the log pair whose gap opens and closes.
- `src/PowerUp.py`: the ghost power-up entity.
- `src/states/PlayingState.py`: now delegates update, input, scoring and game-over to the current mode.
- `src/states/TitleScreenState.py`: the Normal / Hard menu.
- `src/states/CountDownState.py`, `src/World.py`, `src/Bird.py`, `src/LogPair.py`, `settings.py`: carrying the mode through, the power-up list, horizontal velocity, and the new assets.
- `assets/graphics/powerup.png`, `assets/sounds/collision_log.wav`, `powerup.wav`, `ghost.ogg`: the power-up sprite and the new sounds.

Everything else keeps the structure of the original study case: `src/FlappyBird.py` for the main loop and the state machine, `src/states/` for the title, countdown, playing and pause states, and `src/Bird.py`, `src/World.py`, `src/LogPair.py` for the play field.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
