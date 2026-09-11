# 07 - Ultimate Fantasy

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un JRPG al estilo Final Fantasy, escrito en Python utilizando `pygame-ce` y el motor Gale.

## Requisitos y cómo ejecutarlo

Necesitas Python 3 y dos dependencias:

```bash
pip install pygame-ce gale-engine
```

Ha sido probado con Python 3.14, `pygame-ce` 2.5.8 y `gale-engine` 1.16.0. Para iniciar, desde este directorio:

```bash
python main.py
```

## Controles

| Tecla | Acción |
|---|---|
| Flechas | Moverse / navegar los menús |
| Enter | Confirmar |
| Espacio | Interactuar con un NPC, avanzar el diálogo |
| Tab | Abrir el menú del grupo |
| P | Pausar |
| Esc | Salir |

## El juego

Guías a un grupo de cuatro personajes que parte de un pueblo en el centro del mapa, con puertas que llevan a cuatro regiones: norte, sur, este y oeste. Caminar sobre pasto alto tiene una probabilidad de una en diez de iniciar una batalla contra tres a cinco enemigos propios de esa región. En la región oeste, cada batalla que empieza tiene a su vez una probabilidad de una en diez de ser el jefe final en vez de un combate normal: una Flor Devoradora de Hombres acompañada de dos enemigos regulares del oeste.

Antes de salir, armas el grupo: un guerrero, un ranger, un sanador y un mago, cada uno con una opción masculina o femenina que cambia su nombre y su sprite. Ganar una batalla reparte experiencia entre los miembros del grupo que sobrevivieron, y con suficiente experiencia un personaje sube de nivel y mejora sus estadísticas. El progreso se guarda en una de tres ranuras desde el menú de pausa.

## Trabajo en esta entrega

### Panel de estado del grupo y curación fuera de batalla

Al presionar Tab se abre `PartyMenuState`, con opciones para ver el panel de estado del grupo y para curar sin necesidad de entrar en combate.

`PartyStatus` muestra un panel por cada miembro del grupo en una grilla 2x2, cada uno con el sprite del personaje, su nivel, HP, XP, estadísticas y acciones. Una acción se muestra con opacidad completa si cura, y atenuada si no, y el panel entero de un personaje muerto se pinta de rojo en vez del gris habitual.

`HealthCaracter` y `HealthTeam` ejecutan la misma acción de curación que un personaje usaría en batalla, de forma individual o sobre todo el grupo, y muestran el resultado a través de `DialogueState`, el mismo cuadro de texto que usa un NPC para hablarte.

### Batalla por tiempo activo (ATB)

El orden de turnos ya no recorre al grupo y a los enemigos en un ciclo fijo. Cada `BattleEntity` tiene ahora su propia estadística `speed_time` (tomada de `baseSpeedTime` en `src/definitions/entity.py`, de modo que un ranger se recupera más rápido que un mago), y descansa ese tiempo tras actuar antes de volver a estar lista para actuar.

`TakeTurnState` es el planificador detrás de esto: mantiene una cola con quien haya terminado de descansar y le da el turno en cuanto nadie más esté a mitad del suyo, así que los turnos de jugador y de enemigos se intercalan en el orden real en que cada uno queda listo. Esos descansos corren sobre `gale.timer.Timer` en vez de dentro del propio `update` de `BattleState`, así que la cuenta sigue avanzando aunque estés eligiendo una acción en el menú, y un enemigo puede actuar antes de que termines de decidir. `SelectActionState` reemplazó al menú de batalla anterior, agregando Run y Nothing junto a las acciones propias de cada personaje.

Una barra dorada debajo de la barra de vida de cada combatiente se va llenando en tiempo real conforme corre su descanso, así puedes ver quién está por actuar.

### Salón del gremio (opcional)

Ahora hay un edificio de gremio en el pueblo. Su huella queda tallada en la misma capa de paredes de la región que ya bloquea el paso contra la valla, y los NPCs aleatorios del pueblo nunca aparecen dentro de ella.

Caminar hasta su puerta empuja `GuildHallState`, un interior pequeño con el mismo tamaño y encuadre que la arena de batalla. Cuatro camas bordean la pared superior, una por cada slot del grupo, y un personaje muerto aparece descansando en su propia cama en vez de caminar con el resto. Interactuar con cualquier cama cura y revive a todo el grupo de una vez.

## Estructura del código

Archivos agregados para esta entrega:

- `src/states/game/PartyMenuState.py`, `PartyStatus.py`: la GUI de estado del grupo.
- `src/states/game/HealthCaracter.py`, `HealthTeam.py`: la curación fuera de batalla.
- `src/states/game/SelectActionState.py`: el menú de acciones en batalla.
- `src/states/game/TakeTurnState.py`: el planificador del ATB.
- `src/states/game/GuildHallState.py`: el interior del salón del gremio.

Archivos modificados:

- `settings.py`, `src/definitions/entity.py`, `src/entity/BattleEntity.py`, `src/entity/Party.py`: la estadística `speed_time` y todo lo que la lee.
- `src/gui/Panel.py`: un color de relleno opcional, usado en el panel del personaje muerto.
- `src/states/game/BattleState.py`: cambió del menú de batalla anterior a `TakeTurnState`, y se agregó la barra de velocidad.
- `src/world/Region.py`, `src/states/entity/PartyWalkState.py`: el edificio del gremio y su puerta.

`src/states/game/BattleMenuState.py` sigue en el proyecto, pero ya nadie lo importa. `SelectActionState` y `TakeTurnState` lo reemplazaron.

Todo lo demás mantiene la estructura del caso de estudio original: `src/world/` para el mapa y sus regiones, `src/states/game/` para los estados de batalla y menús, `src/states/entity/` para cómo se mueven el grupo y los NPCs, y `src/entity/` para las estadísticas del grupo y los enemigos.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
