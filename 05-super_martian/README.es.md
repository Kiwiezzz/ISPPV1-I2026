# 05 - Super Martian

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un plataformas de desplazamiento lateral (side-scrolling) estilo Super Mario, escrito en Python utilizando `pygame-ce` y el motor Gale.

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
| Flechas o A / D | Moverse a izquierda y derecha |
| Espacio o clic izquierdo | Saltar |
| P | Pausar |
| Enter | Confirmar (menús) |
| Esc | Salir |

El salto tiene altura variable: presiona rápido para un salto corto, o mantén presionado para alcanzar la altura máxima.

## El juego

Corres y saltas a través de dos niveles recolectando monedas antes de que se acabe el tiempo. Las monedas valen 1, 5, 20 o 50 puntos dependiendo de su color, y reaparecen unos segundos después de recogerlas. Cada nivel tiene un temporizador que comienza en 150 segundos; si llega a cero, o si caes por la parte inferior del mapa, mueres.

Dos tipos de criaturas se interponen en tu camino: caracoles que caminan por el suelo y criaturas que vuelan cruzando el nivel de un lado a otro. Saltar sobre una criatura voladora la derriba y te da 50 puntos. Saltar sobre un caracol hace que se esconda en su caparazón durante unos segundos en lugar de morir, y mientras está escondido o cayendo ya no puede hacerte daño. Chocar con una criatura de cualquier otra forma te mata.

## Trabajo en esta entrega

### Nuevo nivel (Tiled)

El nivel 1 es un nuevo nivel creado con Tiled (`assets/tilemaps/level1.json`, de 100 x 12 casillas). Tiene su propio diseño, su propio conjunto de monedas y caracoles, y el bloque clave que se describe a continuación. Se basa en `tileset2.png` y `tileset.png`.

### Bloque de llave y llave

El Nivel 1 contiene una casilla especial marcada en Tiled con la propiedad `is_key`, ubicada dos columnas a la derecha y tres filas hacia arriba de donde comienza el jugador. Se comporta como un bloque completamente sólido: no puedes atravesarlo, y golpearlo desde abajo con la cabeza lo activa.

La comprobación se encuentra en `GameEntity.update`: cuando la entidad se mueve hacia arriba y choca contra una casilla sobre su cabeza, lee dicha casilla y, si tiene `is_key`, llama a `on_hit_key_block`. `Player` sobrescribe ese método. `PlayState` encuentra el bloque cuando se carga el nivel, recuerda su posición e ID de casilla, y luego lo oculta limpiando esa celda, de modo que el bloque solo aparece una vez que se alcanza el objetivo de puntuación.

Cuando golpeas el bloque revelado, `Player.on_hit_key_block` reproduce el sonido del bloque de interrogación y crea un objeto `Key` (llave) en la posición del bloque. La llave comienza completamente oculta dentro del bloque y se eleva 16 píxeles durante medio segundo con una interpolación (tween) `out_cubic`. Su método `render` usa un *stencil* (plantilla) para que solo se dibuje la parte que ya salió del bloque, lo que da la ilusión de que la llave está emergiendo de él. La llave no se puede recoger hasta que termina el tween.

Recoger la llave finaliza el nivel.

### Objetivo de puntuación y victoria

`settings.KEY_SCORE_TARGET` es 450. El HUD muestra tu progreso como `Score: X/450`.

Cuando alcanzas el objetivo, el bloque de la llave aparece, el temporizador se detiene, las monedas dejan de sumar puntos, y las criaturas ya no pueden lastimarte. Aún puedes moverte, así que caminas hacia el bloque, saltas para golpearlo y recoges la llave que sale.

Al recoger la llave se reproduce el sonido de victoria, se congela al jugador y la pantalla se desvanece a negro durante 3.5 segundos antes de cargar el siguiente nivel, o la pantalla final después del nivel 2. Entrar a un nivel ejecuta la misma superposición a la inversa, desvaneciéndose desde negro durante medio segundo.

### Estado de caparazón del caracol

`SnailHiddenState` es el estado en el que entra un caracol después de ser pisado. Detiene al caracol, cambia su animación a la del caparazón, y después de tres segundos lo envía de vuelta a caminar en la misma dirección a la que estaba mirando.

## Estructura del código

Archivos que añadí o modifiqué para esta entrega:

- `assets/tilemaps/level1.json`: el nuevo nivel, incluyendo el bloque de la llave.
- `assets/graphics/key.png`, `assets/sounds/hit_block.wav`, `hit_question_block.wav`, `victory.wav`: el sprite de la llave y los nuevos efectos de sonido.
- `src/Key.py`: el objeto llave, su tween de emergencia y el renderizado con stencil.
- `src/states/entities/creatures_states/SnailHidden.py`: el estado del caparazón del caracol.
- `src/GameEntity.py`: la comprobación de la casilla `is_key` por encima y el *hook* `on_hit_key_block`.
- `src/Player.py`: `on_hit_key_block`, que genera la llave.
- `src/states/game_states/PlayState.py`: la lógica para ocultar y revelar el bloque de la llave, la puntuación, la victoria, el manejo de pisadas y las transiciones de fundido.
- `src/definitions/creatures.py`: el estado `hidden` y la animación para ambos tipos de caracol.
- `settings.py`: las nuevas texturas, sonidos, `NUM_LEVELS`, `KEY_SCORE_TARGET` y tamaño de ventana.

Todo lo demás mantiene la estructura del caso de estudio original: `src/states/` para las máquinas de estado del juego y entidades, `src/mixins/` para el comportamiento dibujable, animado y colisionable compartido por entidades, `GameEntity.py` y `Player.py` para movimiento y colisiones, y `GameLevel.py` para cargar un mapa Tiled y sus criaturas y monedas.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
