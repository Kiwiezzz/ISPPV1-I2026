# 03 - Breakout

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un rompeladrillos estilo Arkanoid, escrito en Python utilizando `pygame-ce` y el motor Gale.

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
| Flechas Izquierda / Derecha | Mover la paleta |
| Espacio | Lanzar la pelota; también pausar |
| F | Disparar los cañones (cuando los tienes) |
| Enter | Confirmar en los menús |
| Esc | Salir |

## El juego

Haz rebotar la pelota contra la paleta para romper todos los ladrillos del nivel sin dejar que la pelota caiga por debajo de la pantalla. Los ladrillos tienen un color y un nivel (tier) del 0 al 3; los de niveles superiores requieren más golpes y otorgan más puntos. Tu puntuación te permite comprar vidas (hasta tres) y alargar la paleta. Cuando un ladrillo se rompe hay un 10% de probabilidad de que suelte un power-up, el cual atrapas tocándolo con la paleta. El juego base ya incluye un power-up que divide la pelota en tres; esta entrega añade tres más.

## Trabajo en esta entrega

Los power-ups se generan desde la fábrica abstracta (abstract factory) de `PlayState` y caen hacia la paleta. Los power-ups temporales (atrapar la pelota, cañones, bomba) muestran una barra de cuenta regresiva con su nombre en la esquina superior izquierda mientras están activos.

### Atrapar la pelota (Catch the ball)

Dura 8 segundos. Mientras está activo, la próxima pelota que toque la paleta se quedará pegada a ella en el punto de contacto en lugar de rebotar, y su velocidad se reducirá a cero. La pelota atascada sigue a la paleta en cada fotograma, manteniendo la distancia horizontal que tenía cuando aterrizó, lo que te permite alinear tu próximo tiro. Presiona Espacio para lanzarla de nuevo con una velocidad aleatoria nueva, de la misma forma en que funciona el estado de saque (serve). Solo se puede retener una pelota a la vez, y si el temporizador se acaba mientras una pelota sigue atascada, esta se lanza por sí sola.

### Cañones (Cannons)

Dura 10 segundos. Mientras está activo, se dibuja un cañón en el borde izquierdo y derecho de la paleta. Presionar la tecla F dispara un cohete (`Rocket`) de cada cañón directamente hacia arriba y reproduce el sonido del cañón. El cohete rompe el primer ladrillo que toca y luego se destruye a sí mismo. No puedes volver a disparar mientras haya algún cohete en la pantalla, por lo que el fuego de cañón se lanza en ráfagas (una salva a la vez).

### Bomba (Bomb - power-up personalizado)

El power-up de libre elección es la Bomba. Le otorga a la pelota un comportamiento altamente explosivo durante 8 segundos.

Mientras está activo, golpear un ladrillo con la pelota le hace el doble de daño, reduciendo su nivel (tier) en 2 de un solo golpe. Inmediatamente después del golpe, se calcula una explosión en una cuadrícula de 3x3 alrededor del ladrillo, y todos los ladrillos en esa área reciben hasta 2 de daño. Un ladrillo débil es destruido en el acto; un ladrillo de nivel superior pierde casi toda su resistencia. La explosión también silencia el sonido normal de rebote y reproduce una fuerte detonación en su lugar, para darle peso al impacto.

`Bomb` hereda de `PowerUp` y sigue el mismo esquema que los otros power-ups temporales, `Cannons` y `CatchTheBall`: una duración de 8 segundos, registrado en `PlayState` mediante `take()` cuando la paleta lo atrapa. El daño de área se resuelve en `PlayState.py`. Este calcula la posición en la cuadrícula `(hit_row, hit_col)` del ladrillo golpeado a partir de su rectángulo de colisión y las proporciones de la cuadrícula `Brickset` (16 de alto por 32 de ancho), y luego recorre las ocho celdas circundantes con dos bucles `for` anidados sobre los desplazamientos `i` y `j`. `Brick.hit` recibe un argumento `play_sound` para que el daño de área pueda aplicarse y sumar puntos sin que nueve ladrillos reproduzcan el sonido de golpe a la vez.

## Estructura del código

Archivos que añadí o modifiqué para esta entrega:

- `src/powerups/CatchTheBall.py`, `src/powerups/Cannons.py`, `src/powerups/Bomb.py`, `src/powerups/__init__.py`: los tres nuevos power-ups.
- `src/Rocket.py`: el proyectil que disparan los cañones.
- `src/states/PlayState.py`: atrapar y lanzar la pelota, disparar y resolver cohetes, el doble golpe y la explosión de 3x3 de la bomba, y el HUD de la cuenta regresiva de power-ups.
- `src/Brick.py`: el parámetro `play_sound` en el método `hit`.
- `settings.py`: los nuevos tipos de power-ups, los *frames* de los cohetes y cañones, y el sonido de la bomba.

Todo lo demás mantiene la estructura del caso de estudio original: `src/Breakout.py` para el bucle principal, `src/states/` para los estados de menú, saque, juego, pausa, victoria, fin del juego y puntuación máxima, y `src/Ball.py`, `src/Paddle.py`, `src/Brick.py`, `src/BrickSet.py` para el campo de juego.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
