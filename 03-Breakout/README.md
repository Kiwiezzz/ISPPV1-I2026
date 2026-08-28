# Breakout - Power-Up Adicional

## Power-Up de Elección Propia: **Bomba (Bomb)**

Como tercer power-up de elección libre, se implementó el power-up **Bomba**. 
Este power-up  dota a la pelota de propiedades altamente explosivas durante un tiempo limitado (8 segundos).

### Mecánica del Power-Up

Mientras el power-up "Bomb" está activo:
1. **Impacto Central Potenciado:** Cuando la pelota golpea un ladrillo, este recibe daño doble (se reduce su tier en 2 unidades de forma instantánea).
2. **Onda Expansiva 3x3:** Inmediatamente después del impacto, ocurre una explosión matemática en una grilla de 3x3 alrededor del ladrillo golpeado.
3. **Daño a Ladrillos Adyacentes:** Todos los ladrillos vecinos dentro del área de la explosión reciben hasta 2 de daño. Es decir, Un ladrillo débil será destruido al instante, mientras que los ladrillos de tier superior perderán gran parte de su resistencia.
4. **Sonidos Únicos:** La explosión silencia el sonido clásico de rebote y lo reemplaza con un sonido de detonación masiva, dando una gran sensación de impacto al jugador.

### Detalles Técnicos de Implementación

- **Clase `Bomb`:** Hereda de `PowerUp`. Utiliza la estructura de los power-ups temporales (similar a `Cannons` y `CatchTheBall`), con una duracion de 8 segundos y registrándose en `PlayState` cuando es atrapado por la paleta (`take()`).
- **Lógica del daño en área** En `PlayState.py`, se calcula dinámicamente la posición `(hit_row, hit_col)` del ladrillo impactado usando su rectángulo de colisión y las proporciones matemáticas de la grilla del `Brickset` (16 de alto x 32 de ancho). A partir de allí, mediante dos ciclos anidados `for` iterando coordenadas `i` y `j` que representan desplazamientos con respecto a la fila y columna del ladrillo impactado.  obtenemos las 8 direcciones adyacentes posibles. El metodo hit se le agrego el parametro play_sound, es decir, `hit(play_sound: bool)` para hacer el daño y sumar los puntos de forma silenciada, evitando que 9 ladrillos reproduzcan el sonido de daño al unísono.

