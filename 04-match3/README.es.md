# 04 - Match 3

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un rompecabezas de combinación de tres (match-3) al estilo Bejeweled, escrito en Python utilizando `pygame-ce` y el motor Gale.

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

Todo el juego se juega con el ratón. Presiona sobre una ficha, arrástrala hacia una ficha vecina y suelta para realizar el movimiento. Haz clic en un power-up para detonarlo en el lugar. `Esc` para salir, `Enter` para confirmar en los menús.

## El juego

El tablero es de 8 por 8. Intercambias fichas adyacentes para alinear tres o más del mismo color; esas fichas desaparecen, las que están encima caen y nuevas fichas caen desde arriba. Las reacciones en cadena siguen sumando puntos hasta que el tablero se estabiliza. Cada nivel te da 260 segundos y un objetivo de puntuación (`nivel * 1.25 * 1000 * 1.5`); alcánzalo para avanzar, si se acaba el tiempo es fin del juego. Los niveles posteriores usan más colores de fichas, por lo que las combinaciones son más difíciles de detectar.

## Trabajo en esta entrega

### Arrastrar y soltar (Drag and drop)

Las fichas se mueven arrastrándolas en lugar de hacer clic dos veces. Cuando presionas el ratón sobre una ficha, esta se convierte en la ficha arrastrada y se guardan su celda inicial y posición en píxeles. Mientras se mantiene presionado el botón, `PlayState.update` establece la posición de la ficha a la posición del ratón en cada fotograma (las coordenadas crudas del ratón se escalan primero del tamaño de la ventana a la resolución virtual), por lo que la ficha sigue al cursor.

Al soltar, `PlayState.on_input` verifica dónde soltaste:

- En la misma celda, y la ficha es un power-up: se activa.
- En una celda adyacente: se intenta el intercambio.
- En cualquier otro lugar: la ficha regresa a donde empezó (mediante un tween).

### Solo se permiten movimientos que formen combinaciones

Cuando sueltas una ficha sobre un vecino, las dos fichas se intercambian en el tablero y `Board.calculate_matches_for` se ejecuta en modo `simulate=True`. Si no encuentra ninguna combinación, se deshace el intercambio y la ficha se desliza de vuelta a su celda. Un movimiento solo se concreta si crea al menos una combinación.

### Reorganización automática del tablero

`Board._initialize_tiles` ya descarta un tablero inicial sin posibles combinaciones y construye otro. Esta entrega extiende esto al transcurso del juego: `Board.has_possible_matches` prueba todos los intercambios horizontales y verticales posibles en el tablero actual y avisa si alguno de ellos generaría una combinación (también devuelve verdadero si hay un power-up en el tablero, ya que siempre puedes hacer clic en él). Después de que un movimiento se asienta y no queda nada por limpiar, `PlayState._calculate_matches` llama a esa verificación y, mientras falle, reconstruye el tablero hasta que aparezca uno jugable.

### Power-ups

Ambos power-ups son subclases de `Tile`, por lo que caen, se pueden arrastrar e intercambiar como cualquier ficha, y pueden quedar atrapados en una combinación posterior. Se encuentran en `src/powerups/`. `Board.calculate_matches_for` crea uno cuando una combinación contiene una línea consecutiva (las filas y las columnas se miden por separado, por lo que una forma de L de cinco fichas no cuenta como una combinación de cinco):

**Bomba de línea (Line bomb)**, a partir de una línea de exactamente 4. Aparece en la celda de la ficha que se movió y conserva el color de esa ficha. Cuando explota, ya sea por un clic directo o por ser parte de una combinación, elimina todas las fichas en su fila y en su columna.

**Bomba de color (Colour bomb)**, a partir de una línea de 5 o más. Misma regla de aparición y regla de color. Cuando explota, elimina todas las fichas de ese color en cualquier parte del tablero.

`Board.remove_matches` recorre la lista de fichas que se están destruyendo y, cada vez que encuentra una bomba, añade los objetivos de esa bomba a la lista. Una bomba atrapada en la explosión de otra bomba también explota, de forma que las reacciones en cadena se propagan. Las fichas destruidas valen 50 puntos cada una, incluidas las añadidas por una reacción en cadena.

## Estructura del código

Archivos que añadí o modifiqué para esta entrega:

- `src/powerups/LineBomb.py`, `src/powerups/ColorBomb.py`, `src/powerups/__init__.py`: las dos fichas de power-up y sus objetivos de explosión.
- `src/Board.py`: generación de power-ups, `has_possible_matches`, el bucle de reorganización, manejo de reacciones en cadena en `remove_matches` y escalado de colores por nivel.
- `src/states/PlayState.py`: la entrada de arrastrar y soltar, la verificación del movimiento de intercambio simulado, la llamada a la reorganización y la activación de los power-ups.
- `src/states/BeginGameState.py`: pasa el nivel al tablero para que este pueda escalar sus colores.
- `assets/graphics/line_bomb.png`, `assets/graphics/Color_bomb.png`, `assets/sounds/bomb.wav`: las superposiciones (overlays) de los power-ups y el sonido de explosión.
- `settings.py`: las nuevas texturas y sonido.

Todo lo demás mantiene la estructura del caso de estudio original: `src/Match3.py` para el bucle principal y la máquina de estados, `src/states/` para los estados del menú, inicio, juego y fin del juego, `src/Board.py` y `src/Tile.py` para la cuadrícula y las fichas.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
