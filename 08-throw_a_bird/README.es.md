# 08 - Throw a Bird

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un juego de artillería con física real al estilo Angry Birds, portado de un proyecto Defold a Python con `pygame-ce`, el gale-engine y su módulo de física basado en Box2D.

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

| Entrada | Acción |
|---|---|
| Arrastrar cerca del ave | Apuntar (soltar para lanzarla) |
| Arrastrar en cualquier otro lugar | Mover la cámara |
| Espacio | Dividir el ave en pleno vuelo |
| Esc | Salir |

## El juego

Hay siempre un ave lista sobre la resortera. La arrastras hacia atrás y la sueltas para lanzarla contra una torre de bloques de piedra y madera que sostienen dos tipos de aliens. La cámara sigue al ave y se aleja mientras más recorre, y una zona de viento espera pasado cada borde del nivel para empujar de vuelta al área de juego cualquier cosa que se aleje demasiado.

Los bloques de piedra y madera se dañan con impactos suficientemente fuertes, mostrando un aspecto agrietado antes de romperse del todo; la madera además esparce algunas astillas al destruirse. Cada ave nueva tiene 50% de probabilidad de salir azul en vez del rojo habitual. Derriba suficiente torre para destruir a todos los aliens y ganas. Haz click en cualquier parte de la pantalla de victoria para intentarlo de nuevo.

## Trabajo en esta entrega

### Dividir el ave en tres

Solo el ave azul tiene esta habilidad. Al presionar espacio mientras está en vuelo, se divide en tres: la original sigue volando con su trayectoria intacta, y dos aves nuevas aparecen junto a ella, con su velocidad rotada 20 grados respecto a la original (una hacia arriba, otra hacia abajo), a la misma rapidez que llevaba en el momento de la división (`PlayState._split_bird`).

Las dos aves nuevas nacen a una pequeña distancia de la original, siguiendo su propio rumbo, en vez de justo encima de ella. `gale.physics.Body.touching_bodies` trata cualquier superposición como una colisión, así que tres aves creadas en el mismo punto exacto se leerían como si ya se hubieran golpeado entre sí antes de que el lanzamiento siquiera continuara.

### La colisión deshabilita la división

Cada ave lleva su propio indicador `has_collided` (`src/entity/Bird.py`), revisado en cada paso de física contra lo que esté tocando en ese momento. En cuanto registra un golpe real, sea el suelo o un bloque, su sprite cambia a un aspecto herido y la habilidad de dividirse se apaga para esa ave por el resto del lanzamiento. Las zonas de viento quedan excluidas de esta revisión: son disparadores invisibles de límite, no algo que el ave realmente haya golpeado, aunque `touching_bodies` también reporte la superposición con ellas.

### El lanzamiento no termina hasta que todas las aves se detienen

`PlayState` ahora sigue a cada ave que sigue en el aire como `self.birds`, no solo a la que inició el lanzamiento. Una ave nueva se carga en la resortera solo cuando todas las de esa lista, la original y las que hayan salido de su división, hayan bajado su velocidad casi por completo; mientras aunque sea una siga en movimiento significativo, el lanzamiento sigue abierto.

## Estructura del código

Archivos modificados para esta entrega:

- `src/entity/Bird.py`: ahora se construye a partir de `BIRDS["red"]` o `BIRDS["blue"]`, lleva `has_collided` y `powerup_activated`, y cambia a su sprite herido en cuanto recibe un golpe.
- `src/definitions/entity.py`: `BIRDS`, con una entrada roja y una azul (la azul más liviana y un poco más pequeña), cada una con su sprite normal y su sprite herido.
- `src/states/game/PlayState.py`: `self.bird` (uno solo) pasó a ser `self.birds` (una lista), más `_spawn_bird` (sortea el color, reconstruye el ave, limpia todas las del lanzamiento anterior) y `_split_bird`.
- `settings.py`: las dos texturas de ave herida, y la tecla espacio ligada a la acción de dividir.

Todo lo demás mantiene la estructura que ya tenía el proyecto: `src/world/Level.py`, `Destructible.py`, `Debris.py` y `Background.py` para la torre, el suelo y las zonas de viento, y `VictoryState` para la pantalla de victoria.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
