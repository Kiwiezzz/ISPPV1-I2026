# 07 - Ultimate Fantasy

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Game made for the Video Game Programming I (ISPPV1) course at Universidad de Los Andes. The base game is a Final Fantasy style JRPG, written in Python on top of `pygame-ce` and the gale-engine.

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
| Arrows | Move / navigate menus |
| Enter | Confirm |
| Space | Interact with an NPC, advance dialogue |
| Tab | Open the party menu |
| P | Pause |
| Esc | Quit |

## The game

You lead a party of four out of a town at the center of the map, with gates leading to four regions: north, south, east and west. Walking through tall grass has a one in ten chance of starting a battle against three to five enemies native to that region. In the west region, a battle starting has its own one in ten chance of being the final boss instead of a regular fight: a Man-Eater Flower backed by two regular west enemies.

Before you set out, you build the party: a warrior, a ranger, a healer and a mage, each with a male or female option that changes their name and sprite. Winning a battle splits experience among the party members who survived it, and enough of it levels a character up, raising their stats. Progress saves to one of three slots from the pause menu.

## Work in this submission

### Party status panel and healing outside battle

Pressing Tab opens `PartyMenuState`, with options for the party status panel and for healing without starting a fight.

`PartyStatus` lays out one panel per party member in a 2x2 grid, each showing that character's sprite, level, HP, XP, stats and actions. An action is shown at full opacity if it heals and dimmed otherwise, and a dead character's whole panel turns red instead of the usual grey.

`HealthCaracter` and `HealthTeam` run the same heal action a character would use in battle, individually or on the whole party, and show the result through `DialogueState`, the same textbox an NPC uses to talk to you.

### Active Time Battle

The battle turn order no longer goes around the party and enemies in a fixed loop. Every `BattleEntity` now has its own `speed_time` stat (set from `baseSpeedTime` in `src/definitions/entity.py`, so a ranger recovers faster than a mage), and rests that long after acting before it is ready to act again.

`TakeTurnState` is the scheduler behind this: it keeps a queue of whoever has finished resting and lets them act as soon as nothing else is mid-turn, so player and enemy turns interleave in whatever order they actually become ready. Those rests run on `gale.timer.Timer` rather than inside `BattleState`'s own `update`, so they keep counting down even while you are choosing an action from the menu, and an enemy can act before you finish deciding. `SelectActionState` replaced the old battle menu, adding Run and Nothing next to each character's own actions.

A gold bar under each combatant's HP bar fills up in real time as their rest counts down, so you can see who is about to act next.

### Guild hall (optional)

A hall building now stands in town. Its footprint is carved into the region's own wall layer, the same one that blocks the party from walking into the fence, and the town's random NPCs never spawn inside it.

Walking up to its door pushes `GuildHallState`, a small interior sized and framed the same way as the battle arena. Four beds line the top wall, one per party slot, and a dead character shows up resting on their own bed instead of walking around with the rest of the group. Interacting with any bed heals and revives the whole party at once.

## Code layout

Files added for this submission:

- `src/states/game/PartyMenuState.py`, `PartyStatus.py`: the party status GUI.
- `src/states/game/HealthCaracter.py`, `HealthTeam.py`: healing outside battle.
- `src/states/game/SelectActionState.py`: the battle action menu.
- `src/states/game/TakeTurnState.py`: the ATB scheduler.
- `src/states/game/GuildHallState.py`: the guild hall interior.

Files changed:

- `settings.py`, `src/definitions/entity.py`, `src/entity/BattleEntity.py`, `src/entity/Party.py`: the `speed_time` stat and everything that reads it.
- `src/gui/Panel.py`: an optional fill color, used for the dead-character panel.
- `src/states/game/BattleState.py`: switched from the old battle menu to `TakeTurnState`, added the speed bar.
- `src/world/Region.py`, `src/states/entity/PartyWalkState.py`: the guild hall building and its door.

`src/states/game/BattleMenuState.py` is still in the project, but nothing imports it anymore. `SelectActionState` and `TakeTurnState` replaced it.

Everything else keeps the structure of the original study case: `src/world/` for the overworld and its regions, `src/states/game/` for battle and menu states, `src/states/entity/` for how the party and NPCs move, and `src/entity/` for party and enemy stats.

## Credits

Original study case and Gale engine: Professor Alejandro Mujica (R3mmurd). The base code in this directory is his. The additions described above are mine.
