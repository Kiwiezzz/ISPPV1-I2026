# 01 - Pong

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un Pong clásico, escrito en Python utilizando `pygame-ce` y el motor Gale.

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
| W / S | Paleta izquierda arriba y abajo |
| Arriba / Abajo | Paleta derecha arriba y abajo |
| Enter | Sacar (serve), y confirmar en la pantalla final |
| Esc | Salir |
| 1 | Iniciar Jugador vs CPU |
| 2 | Iniciar Jugador 1 vs Jugador 2 |
| 3 | Iniciar CPU vs CPU |
| 4 | Salir desde el menú |

El primer jugador en llegar a 5 puntos gana.

## El juego

Dos paletas, una pelota, y la pelota acelera un poco en cada golpe de paleta. La pantalla de título elige quién controla cada paleta antes del saque.

## Trabajo en esta entrega

### Paleta controlada por IA (AI paddle)

Cada paleta tiene una bandera (flag) en el objeto `pong` que indica si la CPU la controla. La pantalla de título establece ambas banderas según la elección en el menú: la opción 1 convierte la paleta derecha en CPU, la opción 3 convierte ambas paletas en CPUs, y la opción 2 deja ambas a los jugadores.

La dirección (steering) se encuentra en `PlayState.update`, justo al lado de donde las paletas leen el teclado, ya que ahí es donde una paleta decide su `vy` en cada fotograma. Una paleta controlada por la CPU solo comienza a reaccionar cuando la pelota se dirige hacia ella y ha cruzado un punto en la mesa (un cuarto del ancho para la paleta derecha, tres cuartos para la izquierda). Hasta entonces se queda quieta, por lo que se compromete a moverse tarde, de la misma forma en que una persona reacciona a un tiro en lugar de seguir la pelota todo el tiempo de un lado a otro.

Una vez que está reaccionando, compara el centro de la pelota con su propio centro:

- Pelota más de `CPU_TOLERANCE` (4 px) por encima del centro de la paleta: `vy = -PADDLE_SPEED`.
- Pelota más de esa distancia por debajo: `vy = PADDLE_SPEED`.
- Dentro de la tolerancia: `vy = 0`.

La tolerancia es una zona muerta alrededor de la línea central que evita que la paleta tiemble hacia arriba y hacia abajo cuando ya está alineada.

La IA juega con las mismas reglas que una persona. Solo escribe `PADDLE_SPEED` o `0` en `vy`, los mismos valores que produce presionar una tecla, por lo que nunca se mueve más rápido que una paleta controlada por un humano. Además, `PlayState.on_input` protege las teclas de cada paleta con una verificación para asegurarse de que no esté controlada por la CPU, por lo que una paleta CPU ignora el teclado por completo.

## Estructura del código

Archivos que incluyen las adiciones:

- `src/states/PlayState.py`: la dirección de la CPU para cada paleta, y la guarda que evita que una paleta CPU también reciba entrada del teclado.
- `src/states/TitleState.py`: el menú de modos y las banderas de CPU para cada paleta que este establece.
- `settings.py`: `CPU_TOLERANCE`, la zona muerta que utiliza la IA.

Todo lo demás mantiene la estructura del caso de estudio original: `src/Pong.py` para el objeto del juego y la máquina de estados, `src/states/` para los estados de título, saque, juego y fin, y `src/Ball.py`, `src/Paddle.py`, `src/rendering.py` para el campo de juego.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
