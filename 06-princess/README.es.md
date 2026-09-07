# 06 - The Legend of the Princess

*Read this in other languages: [English](README.md), [Español](README.es.md).*

Juego creado para el curso de Programación de Videojuegos I (ISPPV1) en la Universidad de Los Andes. El juego base es un ARPG de mazmorras estilo 16-bits, escrito en Python utilizando `pygame-ce` y el motor Gale.

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
| Flechas o WASD | Moverse |
| Espacio | Espada |
| E | Disparar una flecha (una vez que tienes el arco) |
| Enter | Interactuar (abrir el cofre) |
| Esc | Salir |

## El juego

Comienzas en una mazmorra cuyas habitaciones se generan al cruzar cada puerta, con una transición de cámara entre ellas. Los enemigos deambulan y te lastiman al contacto (esqueletos, slimes, murciélagos, fantasmas y arañas), y puedes levantar y lanzar los jarrones del suelo.

En algún momento aparecerá la sala del cofre. Al abrir el cofre obtienes el arco, y desde ese momento puedes disparar flechas además de usar la espada. Una vez que tienes el arco, cruzar una puerta puede llevarte a la sala del jefe.

## Trabajo en esta entrega

### Sistema de cofre y arco

El cofre se genera una vez, al azar, en su propia habitación (`ChestRoom`). Se abre cuando el jugador se sitúa justo debajo de él, mirando hacia arriba, y presiona Enter. Entonces se reproduce una breve animación en la que el personaje levanta el arco, reutilizando el estado `pot-lift` que ya existía para los jarrones.

El disparo está construido con el patrón Factory, como lo requería la asignación:

- `Arrow` es un `GameObject` que representa la flecha. Su estado interno (`left`, `right`, `up`, `down`) elige la textura ya rotada en `settings.py`.
- `Bow` contiene un `Factory(Arrow)` y expone `fire(x, y, direction)`, lo cual crea la flecha con el factory y devuelve un `Projectile` listo para añadir a la habitación.
- El jugador mantiene una instancia de `Bow` en `self.bow`. El estado `PlayerBowState` calcula el punto de aparición a partir de la dirección y llama a `self.entity.bow.fire(...)`.

Mientras el jugador tiene el arco equipado, las animaciones de caminar y reposo utilizan la hoja de sprites con el arco en la mano. Al usar la espada o levantar un jarrón, este se guarda de nuevo.

### Habitación y jefe

La sala del jefe (`BossRoom`) no tiene enemigos, jarrones ni interruptores, y solo mantiene la puerta por la que entraste. Los otros tres lados siguen siendo paredes sólidas. El jefe aparece en el lado opuesto a esa puerta. Cuando entras, la puerta se cierra y se vuelve a abrir cuando el jefe muere.

El jefe es un gólem de fuego. Su comportamiento:

- Se mueve erráticamente y un poco más rápido que el jugador, utilizando la misma lógica de IA que los otros enemigos (`BossWalkState`, `BossIdleState`).
- Cada pocos segundos lanza una bola de fuego (`Fireball`) al punto donde estaba el jugador en ese momento. La bola de fuego viaja en línea recta y no te persigue. Si te alcanza, mueres.
- Tocar su cuerpo cuesta un corazón entero.
- Es inmune a la espada. En su estado normal solo le hacen daño las flechas.
- Cuando una flecha lo impacta, pasa cinco segundos en estado vulnerable: cambia a la paleta de colores invertida, y durante esa ventana la espada sí le hace daño. En el último segundo parpadea entre el aspecto invertido y el normal antes de volver a la normalidad. Mientras es vulnerable se queda quieto y no dispara.

## Estructura del código

Archivos que añadí o modifiqué para esta entrega:

- `src/Arrow.py`, `src/Bow.py`: la flecha y el arco con el factory.
- `src/Fireball.py`: el proyectil del jefe.
- `src/states/entity/BossWalkState.py`, `BossIdleState.py`, `BossInvertedState.py`: los estados del jefe.
- `src/states/entity/player/PlayerBowState.py`: el estado de disparo del jugador.
- `src/world/BossRoom.py`: la sala del jefe y el manejo de sus bolas de fuego.
- `src/world/ChestRoom.py`, `Dungeon.py`, `Room.py`, `Player.py`, `settings.py` y `definitions/entity.py`: cambios para conectar todo lo anterior.

Todo lo demás mantiene la estructura del caso de estudio original: `src/world/` para el mapa y las habitaciones, `src/states/` para las máquinas de estado del juego y entidades, y `Entity.py` con `Player.py` para movimiento, colisiones, animación y salud.

## Créditos

Caso de estudio original y motor Gale: Profesor Alejandro Mujica (R3mmurd). El código base en este directorio es suyo. Las adiciones descritas anteriormente son mías.
