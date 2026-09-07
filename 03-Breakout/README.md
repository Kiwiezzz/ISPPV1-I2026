# 03 - Breakout

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is an Arkanoid style brick breaker, written in Python on top of `pygame-ce` and the Gale engine.

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
| Left / Right arrows | Move the paddle |
| Space | Launch the ball; also pause |
| F | Fire the cannons (when you have them) |
| Enter | Confirm on menus |
| Esc | Quit |

## The game

Bounce the ball off the paddle to break every brick in the level without letting the ball fall past the bottom. Bricks have a colour and a tier from 0 to 3; higher tiers take more hits and are worth more points. Your score buys back lives (up to three) and grows the paddle. When a brick breaks there is a 10% chance it drops a power-up, which you catch by touching it with the paddle. The base game already includes a power-up that splits the ball into three; this submission adds three more.

## Work in this submission

Power-ups spawn from `PlayState`'s abstract factory and fall toward the paddle. The timed ones (catch, cannons, bomb) show a labelled countdown bar in the top-left corner while they are active.

### Catch the ball

Lasts 8 seconds. While it is active, the next ball that touches the paddle sticks to it at the point of contact instead of bouncing, with its velocity zeroed. The stuck ball tracks the paddle every frame, keeping the horizontal offset it had when it landed, so you can line up your next shot. Press Space to launch it again with a fresh random velocity, the same way the serve state works. Only one ball can be held at a time, and if the timer runs out while a ball is still stuck it launches on its own.

### Cannons

Lasts 10 seconds. While active, a cannon is drawn at the left and right edge of the paddle. Pressing F fires one `Rocket` from each cannon, straight up, and plays the cannon sound. A rocket breaks the first brick it touches and then destroys itself. You cannot fire again while any rockets are still on screen, so cannon fire comes one salvo at a time.

### Bomb (custom power-up)

The free-choice power-up is the Bomb. It gives the ball highly explosive behaviour for 8 seconds.

While it is active, hitting a brick with the ball does double damage to that brick, dropping its tier by 2 at once. Right after the hit, an explosion is computed over the 3x3 grid around the brick, and every brick in that area takes up to 2 damage. A weak brick is destroyed on the spot; a higher-tier brick loses most of its resistance. The explosion also mutes the normal bounce sound and plays a heavy detonation in its place, so the hit lands with weight.

`Bomb` extends `PowerUp` and follows the same shape as the other timed power-ups, `Cannons` and `CatchTheBall`: an 8-second duration, registered on `PlayState` through `take()` when the paddle catches it. The area damage is resolved in `PlayState.py`. It works out the hit brick's grid position `(hit_row, hit_col)` from its collision rectangle and the proportions of the `Brickset` grid (16 tall by 32 wide), then walks the eight surrounding cells with two nested `for` loops over the offsets `i` and `j`. `Brick.hit` takes a `play_sound` argument so the area damage can apply and score without nine bricks playing the hit sound at once.

## Code layout

Files added or changed for this submission:

- `src/powerups/CatchTheBall.py`, `src/powerups/Cannons.py`, `src/powerups/Bomb.py`, `src/powerups/__init__.py`: the three new power-ups.
- `src/Rocket.py`: the projectile the cannons fire.
- `src/states/PlayState.py`: catching and launching the ball, firing and resolving rockets, the bomb's double hit and 3x3 blast, and the power-up countdown HUD.
- `src/Brick.py`: the `play_sound` parameter on `hit`.
- `settings.py`: the new power-up types, the rocket and cannon frames, and the bomb sound.

Everything else keeps the structure of the original study case: `src/Breakout.py` for the main loop, `src/states/` for the menu, serve, play, pause, victory, game-over and high-score states, and `src/Ball.py`, `src/Paddle.py`, `src/Brick.py`, `src/BrickSet.py` for the play field.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
