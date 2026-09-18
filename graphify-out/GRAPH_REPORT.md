# Graph Report - The-Whistle  (2026-09-15)

## Corpus Check
- 109 files · ~115,671 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 672 nodes · 1062 edges · 89 communities (38 shown, 48 thin omitted)
- Extraction: 92% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.9)
- Token cost: 1,731,174 input · 0 output

## Community Hubs (Navigation)
- Global Settings & Assets
- Rooms & Doors
- Command Pattern (Input to Action)
- Monster Base Architecture
- Audio Manager & Playback
- Changelog: Core Refactors
- Player Entity Core
- Game Bootstrap & Start
- Monster Entity Core
- Objective State UI
- Interactive Item Definitions
- A* Pathfinding System
- Player State Machine Base
- Changelog: Lighting & Architecture
- Play State (Main Loop)
- Crowbar Minigame
- Base Game Object
- Changelog: Minigames System
- Base Entity Class
- Fuse Box Minigame
- Safe Minigame
- README: Bilingual & Setup
- Monster Moving-To-Door State
- Game Over State
- Changelog: AI & FSM
- Changelog: Audio System
- Entity Animation Frames
- Monster Knocking State
- Note Reading State
- Victory State
- Changelog: Command Pattern
- Changelog: Rooms & Hiding
- Changelog: Survival Balance
- Lockpick Minigame
- Player Animation & Inventory Cycle
- Monster Patrol State
- Tiled Map Loading
- Changelog: Monster Sprite Fixes
- Player Rendering
- Jumpscare Images (El Silbon)
- Player Equipped Item
- Monster State Machine Init
- Player State Machine Init
- Monster Idle Sprite
- Monster Running Sprite
- Monster Walk Sprite
- Boss Enemy Idle Sprite (Placeholder)
- Placeholder Idle Sprite 5
- Placeholder Idle Sprite 6
- Placeholder Idle Sprite 7
- Placeholder Idle Sprite 8
- Boss Enemy Stomp Sprite (Placeholder)
- Placeholder Stomp Sprite 10
- Placeholder Stomp Sprite 11
- Placeholder Stomp Sprite 12
- Placeholder Stomp Sprite 9
- Boss Enemy Swipe Sprite (Placeholder)
- Placeholder Swipe Sprite 13
- Placeholder Swipe Sprite 14
- Placeholder Swipe Sprite 15
- Placeholder Swipe Sprite 16
- Boss Enemy Walk Sprite (Placeholder)
- Placeholder Walk Sprite 2
- Placeholder Walk Sprite 3
- Placeholder Walk Sprite 4
- Placeholder Walk Spritesheet
- El Silbon Idle Sprite (Final Art)
- El Silbon Walk Sprite (Final Art)
- Andreas Dying Sprite
- Andreas Idle Sprite
- Andreas Walk-Left Sprite
- Andreas Walk-Right Sprite
- Andreas Walk-Back Sprite
- Andreas Walk-Down Sprite
- Environment Tileset Sprite
- Changelog: Compact HUD Inventory
- Changelog: Door Traversal AI
- Changelog: Jumpscare System
- Changelog: Level Collision Polish
- Changelog: Multi-Slot Inventory HUD
- Changelog: Perimeter Wall Fix
- Changelog: Movement Key Sync Fix
- Changelog: Pygame Subsurface Fix
- Changelog: Sprite Assets Added
- Changelog: Tiled Map Adjustments
- Changelog: Dialogue Typography

## God Nodes (most connected - your core abstractions)
1. `PlayState` - 34 edges
2. `Player` - 31 edges
3. `Monster` - 26 edges
4. `t()` - 23 edges
5. `MonsterBaseState` - 21 edges
6. `BaseMinigame` - 18 edges
7. `Door` - 17 edges
8. `House` - 16 edges
9. `Room` - 16 edges
10. `StartState` - 13 edges

## Surprising Connections (you probably didn't know these)
- `BaseEntity shared hierarchy (Player, Monster, NPC)` --references--> `Legacy NPC code removal and cleanup`  [AMBIGUOUS]
  README.md → CHANGELOG.md
- `Pygame library` --conceptually_related_to--> `pygame (>=2.6.0)`  [INFERRED]
  README.md → requirements.txt
- `Gale engine library` --conceptually_related_to--> `gale`  [INFERRED]
  README.md → requirements.txt
- `Flashlight and light cone mechanic` --references--> `Flashlight battery rebalance (0.2.0)`  [EXTRACTED]
  README.md → CHANGELOG.md
- `Flashlight and light cone mechanic` --references--> `Generic light-source system (src/systems/LightingSystem.py, gale.stencil.Stencil)`  [EXTRACTED]
  README.md → CHANGELOG.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Active overlay minigames sharing the BaseMinigame lifecycle** — changelog_baseminigame, changelog_safeminigame, changelog_lockpickminigame, changelog_crowbarminigame, changelog_fuseboxminigame [EXTRACTED 1.00]
- **Non-linear puzzle dependency chain (Lockpick to Old Key to Forest Exit Key, plus Crowbar)** — changelog_lockpick_item, changelog_old_key_item, changelog_forest_exit_key_item, changelog_crowbar_item, changelog_npc_progression_puzzle_chain [EXTRACTED 1.00]
- **Command pattern architecture shared conceptually with the 06-princess project** — changelog_command_pattern, changelog_06princess_gale_command, changelog_princess_entitywalkstate [INFERRED 0.85]

## Communities (89 total, 48 thin omitted)

### Community 0 - "Global Settings & Assets"
Cohesion: 0.05
Nodes (43): play_music(), play_sound(), El Silbón: Nightmare at the Cabin (2D Survival Horror) Global configurations,…, Plays a sound clip with specified volume and optional dedicated channel., Plays background ambient music on loop., Stops audio playback on the specified channel., Updates the volume of a specific audio channel in real-time., Stops playback on all active audio channels. (+35 more)

### Community 1 - "Rooms & Doors"
Cohesion: 0.06
Nodes (30): Layout data for every room in the cabin: which Tiled map backs it, its…, Door, Rect, Surface, Door class for room interconnections, supporting locks and wooden barricades., GameObject, GameObject and ThrowableProjectile classes for items, tools, and interactable…, HidingSpot (+22 more)

### Community 2 - "Command Pattern (Input to Action)"
Cohesion: 0.06
Nodes (24): Command, BerserkCommand, ChaseCommand, CycleItemCommand, FlashlightCommand, InteractCommand, MoveDownCommand, MoveLeftCommand (+16 more)

### Community 3 - "Monster Base Architecture"
Cohesion: 0.09
Nodes (15): Sprite/animation specs for Player and Monster, plus build_animations, a loader…, Monster entity class (El Silbón). AI decision-making lives in the per-state…, MonsterBaseState, BaseState, Surface, MonsterBerserkState, Enraged pursuit, triggered by a chance roll when hit by a thrown object., MonsterChaseState (+7 more)

### Community 4 - "Audio Manager & Playback"
Cohesion: 0.08
Nodes (14): AudioManager, Starts looping atmospheric cabin background music if not already playing., Plays a single burst of the folklore whistle on its dedicated channel., Stops whistling playback., Plays the door knock sound effect before the monster bursts in., Plays both jumpscare effects (jumpscare1 and jumpscare2) simultaneously while…, Modulates whistling volume, breathing, and footsteps in real-time: - Periodic…, LightingSystem (+6 more)

### Community 5 - "Changelog: Core Refactors"
Cohesion: 0.10
Nodes (23): build_animations() now returns animations and textures, Missing cabinet/safe sprite and label fix, Crowbar item, Data-driven definitions package (src/definitions/), Duplicate NPC initialization fix, entity.py animation specs and build_animations() loader, Forest Exit Key item, GameObject dropped the name constructor parameter (+15 more)

### Community 6 - "Player Entity Core"
Cohesion: 0.13
Nodes (7): Player, Rect, Adds an item to inventory without overwriting existing items., Removes an item from inventory (e.g. consumed keys)., Checks if player possesses the given item in any inventory slot., Completely halts movement and clears all held directional inputs, running…, Synchronizes movement and run states with actual physical keyboard state.

### Community 7 - "Game Bootstrap & Start"
Cohesion: 0.13
Nodes (8): Game, BaseState, InputData, StartState, InputData, Surface, Main game class ElSilbonGame based on gale.game.Game and gale.state.StateStack., TheWhistle

### Community 8 - "Monster Entity Core"
Cohesion: 0.15
Nodes (8): Monster, Rect, Surface, Moves towards target coordinate with obstacle avoidance., Renders the current animation frame horizontally centered over the collision…, Alerts the monster of a sound if within audio radius., Applies 75% Stun / 25% Berserk probability., Checks whether the player is currently detected by line of sight or flashlight.

### Community 9 - "Objective State UI"
Cohesion: 0.12
Nodes (9): ObjectiveState, BaseState, InputData, Surface, PauseState, BaseState, InputData, Surface (+1 more)

### Community 10 - "Interactive Item Definitions"
Cohesion: 0.29
Nodes (16): _draw_battery(), _draw_cabinet(), _draw_crowbar(), _draw_fuse_box(), _draw_fuse_key(), _draw_key(), _draw_lockpick(), _draw_note() (+8 more)

### Community 11 - "A* Pathfinding System"
Cohesion: 0.17
Nodes (15): _build_walkable_grid(), find_path(), _has_clear_line(), _nearest_walkable_cell(), _octile_distance(), Grid-based A* pathfinding for a Room, so a monster walking toward a point can…, Collapses the raw, staircase-y cell-by-cell route into just its corners: as…, If `cell` itself isn't walkable (e.g. it fell inside an obstacle's safety… (+7 more)

### Community 12 - "Player State Machine Base"
Cohesion: 0.27
Nodes (6): Player class (Paramedic protagonist - Andreas). Manages directional movement…, PlayerBaseState, BaseState, PlayerHidingState, PlayerIdleState, PlayerWalkState

### Community 13 - "Changelog: Lighting & Architecture"
Cohesion: 0.18
Nodes (12): Removed redundant src/states/game/BaseState.py, Broken imports after src/states -> src/states/game move fix, Smooth camera tracking system, Core architecture and state stack (0.1.0), Dynamic lighting and darkness (pygame darkness-mask blending) (0.1.0), Rationale: each light's darkness removal and its own color cast are controlled independently, so any new light source is just another list entry with no renderer changes needed, Generic light-source system (src/systems/LightingSystem.py, gale.stencil.Stencil), Monster.ai_state never reflected current state fix (+4 more)

### Community 14 - "Play State (Main Loop)"
Cohesion: 0.23
Nodes (4): PlayState, BaseState, Surface, Builds this frame's list of active lights -- the player's flashlight (or a dim…

### Community 15 - "Crowbar Minigame"
Cohesion: 0.35
Nodes (4): CrowbarMinigame, Any, Event, Surface

### Community 16 - "Base Game Object"
Cohesion: 0.24
Nodes (5): Rect, Surface, Projectile thrown by the player to stun or enrage El Silbón, or distract him…, Updates projectile position. Returns True if projectile impacted an obstacle or…, ThrowableProjectile

### Community 17 - "Changelog: Minigames System"
Cohesion: 0.20
Nodes (9): BaseMinigame abstract lifecycle base class, CrowbarMinigame button-mash prying puzzle, Fuse Box interactable object, Fuse Box Key and locked electrical cabinet, FuseBoxMinigame wire patching puzzle, LockpickMinigame tension lockpicking puzzle, Real-Time Active Overlay Minigames System, SafeMinigame rotary combination safe puzzle (+1 more)

### Community 18 - "Base Entity Class"
Cohesion: 0.22
Nodes (4): BaseEntity, Rect, Surface, BaseEntity class for all movable entities (Player, Monster).

### Community 19 - "Fuse Box Minigame"
Cohesion: 0.36
Nodes (4): FuseBoxMinigame, Any, Event, Surface

### Community 20 - "Safe Minigame"
Cohesion: 0.36
Nodes (4): Any, Event, Surface, SafeMinigame

### Community 21 - "README: Bilingual & Setup"
Cohesion: 0.25
Nodes (9): Internationalization (es/en) (0.1.0), Bilingual Spanish/English system, Project Developers (Francisco Grimaldo and Isaac Montes), El Silbon - 2D Top-Down Survival Horror, Gale engine library, Installation and setup instructions, Pygame library, gale (+1 more)

### Community 22 - "Monster Moving-To-Door State"
Cohesion: 0.25
Nodes (4): MonsterMovingToDoorState, Envuelve una Room pero le esconde una puerta puntual a get_obstacles() -- así…, Physically pathfinds and walks to a chosen door before transitioning rooms,…, _RoomWithoutDoor

### Community 23 - "Game Over State"
Cohesion: 0.25
Nodes (4): GameOverState, BaseState, InputData, Surface

### Community 24 - "Changelog: AI & FSM"
Cohesion: 0.29
Nodes (8): Grid-based A* pathfinding (src/systems/Pathfinding.py), Rationale: A* rebuilds a cheap per-call grid since rooms are small, and pads obstacles by half the entity's width so a path never threads a gap the body could not fit through, Entity and AI systems (Player, Monster FSM, NPC) (0.1.0), Player facing wrong direction while walking diagonally fix, Player and Monster finite state machines, Silbon AI physical door transit (SilbonMovingToDoorState), Silbon zombie state and knocking vulnerability fix, BaseEntity shared hierarchy (Player, Monster, NPC)

### Community 25 - "Changelog: Audio System"
Cohesion: 0.36
Nodes (8): Audio revision and sound assets (0.3.0), 16-channel audio system (0.1.0), Door listening mechanic and ambient ducking, El Silbon stalking and running footstep audio, El Silbon footstep audio persisting on Game Over fix, Dedicated minigame audio channel (Channel 8), AudioManager (spatial whistle and sfx modulation), Whistle Paradox folklore mechanic

### Community 26 - "Entity Animation Frames"
Cohesion: 0.25
Nodes (8): frame(), Rect, build_animations(), _fallback_frame(), Animation, Any, Surface, :returns: (animations, textures) -- animations[name] plays back settings.FRAMES…

### Community 27 - "Monster Knocking State"
Cohesion: 0.29
Nodes (3): Animation, MonsterKnockingState, Knocks loudly on a door before entering the target room, giving the player a…

### Community 28 - "Note Reading State"
Cohesion: 0.29
Nodes (4): NoteState, BaseState, InputData, Surface

### Community 29 - "Victory State"
Cohesion: 0.29
Nodes (4): BaseState, InputData, Surface, VictoryState

### Community 30 - "Changelog: Command Pattern"
Cohesion: 0.29
Nodes (7): 06-princess project gale.command usage (external reference), Command pattern for Andreas and El Silbon (src/commands.py), Rationale: direct state calls kept for transitions needing extra per-call data a fixed command signature cannot carry, Player held movement dict resolved by update_movement, Player edge-triggered interact/throw request flags, PlayState.on_input command dispatch refactor, 06-princess EntityWalkState AI command firing pattern (external reference)

### Community 31 - "Changelog: Rooms & Hiding"
Cohesion: 0.33
Nodes (7): 8-Room house expansion and continuous 360 loop layout, Tactical throwable obstacle collisions and noise distraction, World and cabin environment (House, Door, HidingSpot, GameObject) (0.1.0), Control scheme (movement, interact, flashlight, throw, objectives, pause), Stealth hiding spots mechanic, House and Room level management, Throwable objects mechanic (stun / berserk)

### Community 32 - "Changelog: Survival Balance"
Cohesion: 0.33
Nodes (7): Flashlight battery rebalance (0.2.0), Dynamic acoustic hearing for El Silbon, Player sprint and footstep cadence (Shift), Silbon AI aggressiveness and reaction rebalance (0.2.0), Survival, movement, and acoustic balance adjustments, Rationale: player base and sprint speed were set below the monster's patrol/chase speed so sprinting is used to reach hiding spots tactically rather than to outrun the threat in a straight corridor, Flashlight and light cone mechanic

### Community 33 - "Lockpick Minigame"
Cohesion: 0.48
Nodes (3): LockpickMinigame, Any, Surface

### Community 34 - "Player Animation & Inventory Cycle"
Cohesion: 0.20
Nodes (3): Animation, Selects an active inventory slot by index (0-4)., Cycles to the next item in inventory.

### Community 37 - "Tiled Map Loading"
Cohesion: 0.40
Nodes (5): Ground floor expansion and Tiled level maps, Multi-floor stair navigation, Authored Tiled doors and transitions (FirstRoom <-> UpperHallway), Tiled JSON map integration and level loader (TiledLevelLoader.py), Tiled Map Editor (room JSON export)

### Community 38 - "Changelog: Monster Sprite Fixes"
Cohesion: 0.50
Nodes (4): MONSTER_ANIMATIONS retargeted to monster_walk/monster_idle art, Monster rendering as solid-color fallback rectangle fix, Monster.render_sprite() dynamic bottom-anchored positioning, New El Silbon sprite artwork

### Community 40 - "Jumpscare Images (El Silbon)"
Cohesion: 0.67
Nodes (3): El Silbon Attack Jumpscare, Silbón Red Flash (jumpscare), El Silbón Jumpscare - Sad Variant

## Ambiguous Edges - Review These
- `BaseEntity shared hierarchy (Player, Monster, NPC)` → `Legacy NPC code removal and cleanup`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **74 isolated node(s):** `Project Developers (Francisco Grimaldo and Isaac Montes)`, `SafeMinigame rotary combination safe puzzle`, `LockpickMinigame tension lockpicking puzzle`, `CrowbarMinigame button-mash prying puzzle`, `Authored Tiled doors and transitions (FirstRoom <-> UpperHallway)` (+69 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 311 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `BaseEntity shared hierarchy (Player, Monster, NPC)` and `Legacy NPC code removal and cleanup`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `PlayState` connect `Play State (Main Loop)` to `Global Settings & Assets`, `Lockpick Minigame`, `Rooms & Doors`, `PlayState Interaction Handlers`, `Audio Manager & Playback`, `Player Entity Core`, `Game Bootstrap & Start`, `Monster Entity Core`, `Objective State UI`, `Crowbar Minigame`, `Base Game Object`, `Fuse Box Minigame`, `Safe Minigame`, `Game Over State`, `Note Reading State`, `Victory State`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `Player` connect `Player Entity Core` to `Global Settings & Assets`, `Player Animation & Inventory Cycle`, `Audio Manager & Playback`, `Player Rendering`, `Player Equipped Item`, `Player State Machine Base`, `Play State (Main Loop)`, `Base Entity Class`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `Monster` connect `Monster Entity Core` to `Global Settings & Assets`, `Monster Patrol State`, `Monster Base Architecture`, `Audio Manager & Playback`, `Play State (Main Loop)`, `Base Entity Class`, `Monster Moving-To-Door State`, `Monster Knocking State`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `PlayState` (e.g. with `Monster` and `Player`) actually correct?**
  _`PlayState` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Player` (e.g. with `PlayerHidingState` and `PlayerIdleState`) actually correct?**
  _`Player` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Monster` (e.g. with `MonsterBerserkState` and `MonsterChaseState`) actually correct?**
  _`Monster` has 9 INFERRED edges - model-reasoned connections that need verification._