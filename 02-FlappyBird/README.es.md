# 02 - Flappy Bird

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un clon de Flappy Bird, escrito en Python utilizando `pygame-ce` y el motor Gale.

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
| Clic izquierdo del ratón | Aletear (Flap) |
| A / D | Mover el pájaro de izquierda a derecha (solo en modo difícil) |
| Esc | Pausar y reanudar |
| W / S o Arriba / Abajo | Moverse por un menú |
| Enter | Confirmar |

## El juego

Aletea para mantener al pájaro en el aire y vuela a través de los espacios entre los pares de troncos sin tocarlos ni tocar el suelo. Cada par que superas vale un punto. Desde la pantalla de título eliges el modo Normal o Difícil (Hard) antes de que comience la cuenta regresiva.

## Trabajo en esta entrega

### Estado de pausa (Pause state)

`PauseState` se alterna con la tecla `Esc`. `PlayingState` reacciona a esa tecla cambiando al estado de pausa y entregándole el mundo (`world`), el pájaro (`bird`), la puntuación (`score`) y el modo de juego (`game_mode`) actuales; `PauseState` reacciona a la misma tecla devolviéndoselos directamente a `PlayingState`. Debido a que el mundo y el pájaro se pasan a través del cambio de estado en lugar de ser reconstruidos, `PlayingState.enter` los reutiliza y el juego continúa exactamente desde donde se detuvo.

La pantalla de pausa también tiene un pequeño menú: Continuar / Reiniciar / Salir, el cual se mueve con `W`/`S` o las flechas y se selecciona con `Enter`. Reiniciar (Restart) y Salir (Exit) limpian el power-up de fantasma en caso de que estuviera activo (la opacidad del pájaro vuelve al máximo, y se restaura la música de fondo).

La asignación pregunta cuáles métodos de estado necesita esto:

- `enter`: sí. Recibe los objetos del juego para mantenerlos y configura el menú.
- `render`: sí. Dibuja el mundo y el pájaro congelados, una superposición oscura, la etiqueta "Paused" y el menú.
- `on_input` (`handle_input`): sí. Alterna de vuelta al juego, mueve la selección del menú y actúa sobre la elección.
- `update`: no. Nada se mueve mientras está en pausa, por lo que no hay nada que avanzar por fotograma.
- `exit`: no. No hay estado que desmontar al salir; todo lo que el siguiente estado necesita se pasó a través de `enter`.

### Modos de juego (Patrón Strategy)

`GameMode` es una base abstracta con los métodos `update`, `is_game_over`, `reset`, `on_score`, `render` y `on_input`. `PlayingState` contiene un `GameMode` y le delega cada una de esas llamadas, por lo que no sabe ni le importa qué modo se está ejecutando. La pantalla de título construye un `NormalMode` o un `HardMode` y lo pasa a través de la cuenta regresiva hacia el juego en sí.

El **modo Normal (Normal mode)** mantiene el comportamiento original. Los pares de troncos aparecen en un temporizador fijo de 1.5 segundos, cada uno desviándose un poco de la altura del anterior, y se construyen mediante un `Factory(LogPair)`. Aletear es la única entrada (input) posible.

El **modo Difícil (Hard mode)** añade:

- **Movimiento horizontal.** `A` y `D` establecen la velocidad horizontal del pájaro, por lo que puedes moverte a lo largo de la pantalla además de hacia arriba y hacia abajo.
- **Obstáculos irregulares.** El intervalo de aparición es aleatorio (entre 1.2 y 2.5 segundos aproximadamente), y también lo es el espacio vertical de cada par. Qué tanto puede variar la altura de un par respecto al anterior está ligado a cuánto tiempo ha pasado desde la última aparición (`(interval - 1.0) * 80`), y el resultado se ajusta (clamp) para que un espacio sea siempre alcanzable desde el anterior.
- **Troncos que se abren y cierran.** Alrededor del 60% de los pares son un `MovingLogPair`, cuyo espacio oscila con una onda senoidal. Cuando el espacio casi se cierra, reproduce un sonido de chasquido una vez.
- **Power-up de fantasma (Ghost).** Creado con un `Factory(PowerUp)` a una altura aleatoria y desplazándose desde la derecha. Recogerlo lo elimina de la escena, vuelve al pájaro semitransparente, reproduce un sonido y cambia la música por la pista del fantasma. Durante 6 segundos, el pájaro atraviesa los troncos (el suelo aún te mata), y los últimos 2 segundos parpadea como advertencia. Cuando se acaba, la opacidad del pájaro y la música vuelven a la normalidad.

`HardMode.is_game_over` refleja esto: el suelo siempre es fatal, y mientras el fantasma está activo se ignoran las colisiones con los troncos.

## Estructura del código

Archivos que añadí o modifiqué para esta entrega:

- `src/states/PauseState.py`: la pantalla de pausa y su menú.
- `src/states/gamemode/GameMode.py`, `NormalMode.py`, `HardMode.py`, `__init__.py`: la base del patrón Strategy y los dos modos.
- `src/MovingLogPair.py`: el par de troncos cuyo espacio se abre y se cierra.
- `src/PowerUp.py`: la entidad del power-up del fantasma.
- `src/states/PlayingState.py`: ahora delega la actualización, la entrada, la puntuación y el fin del juego al modo actual.
- `src/states/TitleScreenState.py`: el menú Normal / Difícil.
- `src/states/CountDownState.py`, `src/World.py`, `src/Bird.py`, `src/LogPair.py`, `settings.py`: la transferencia del modo a lo largo de los estados, la lista de power-ups, la velocidad horizontal y los nuevos *assets*.
- `assets/graphics/powerup.png`, `assets/sounds/collision_log.wav`, `powerup.wav`, `ghost.ogg`: el sprite del power-up y los nuevos sonidos.

Todo lo demás mantiene la estructura del caso de estudio original: `src/FlappyBird.py` para el bucle principal y la máquina de estados, `src/states/` para los estados de título, cuenta regresiva, juego y pausa, y `src/Bird.py`, `src/World.py`, `src/LogPair.py` para el campo de juego.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
