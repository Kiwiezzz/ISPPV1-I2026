# 01 - Pong

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is a classic Pong, written in Python on top of `pygame-ce` and the Gale engine.

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
| W / S | Left paddle up and down |
| Up / Down | Right paddle up and down |
| Enter | Serve, and confirm on the end screen |
| Esc | Quit |
| 1 | Start Player vs CPU |
| 2 | Start Player 1 vs Player 2 |
| 3 | Start CPU vs CPU |
| 4 | Quit from the menu |

First player to 5 points wins.

## The game

Two paddles, one ball, and the ball speeds up a little on every paddle hit. The title screen picks who controls each paddle before the serve.

## Work in this submission

### AI paddle

Each paddle has a flag on the `pong` object saying whether the CPU controls it. The title screen sets both flags from the menu choice: option 1 makes the right paddle a CPU, option 3 makes both paddles CPUs, option 2 leaves both to the players.

The steering sits in `PlayState.update`, right next to where the paddles read the keyboard, since that is where a paddle decides its `vy` each frame. A CPU paddle only starts reacting once the ball is heading its way and has crossed a point on the table (a quarter of the width for the right paddle, three quarters for the left). Until then it holds still, so it commits to a move late, the way a person reacts to a shot instead of shadowing the ball the whole way across.

Once it is reacting, it compares the ball's centre with its own centre:

- Ball more than `CPU_TOLERANCE` (4 px) above the paddle centre: `vy = -PADDLE_SPEED`.
- Ball more than that below: `vy = PADDLE_SPEED`.
- Within the tolerance: `vy = 0`.

The tolerance is a dead zone around the centre line that keeps the paddle from twitching up and down when it is already lined up.

The AI plays by the same rules as a person. It only ever writes `PADDLE_SPEED` or `0` into `vy`, the same values a key press produces, so it never moves faster than a human paddle. And `PlayState.on_input` guards each paddle's keys with a check that the paddle is not CPU-controlled, so a CPU paddle ignores the keyboard entirely.

## Code layout

Files that carry the additions:

- `src/states/PlayState.py`: the CPU steering for each paddle, and the guard that stops a CPU paddle from also taking keyboard input.
- `src/states/TitleState.py`: the mode menu and the per-paddle CPU flags it sets.
- `settings.py`: `CPU_TOLERANCE`, the dead zone the AI uses.

Everything else keeps the structure of the original study case: `src/Pong.py` for the game object and the state machine, `src/states/` for the title, serve, play and done states, and `src/Ball.py`, `src/Paddle.py`, `src/rendering.py` for the play field.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
