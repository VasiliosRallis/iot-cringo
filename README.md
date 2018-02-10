# embedded_cw1
IOT coursework - Cringo device

- Cringo device is an IOT concept which emulates a classic game, Bingo.
- It uses an ambient light sensor to set the seed for the RNG and then generates a sequence of random numbers
from 1 to 90 (included) on demand. Reading for the ambient light sensor, since it depends on the background light
provides a true random seed for the generator hence produces a true random sequence, compared to the traditional
seeding which generates pseudorandom sequences.
- It provides a simple and intuitive user interface thanks to the proximity sensor which is used to detect if someone has
his finger close or touching the sensor and for how long.
- A short touch allows the user to move to the next state, while after the game finishes, a long touch of the sensor
restarts the game.
- Messages regarding the wifi and game status as well as the generated numbers are printed on OLED screen with aim to
improve further the user experience.
- The design of the device follows a futuristic, minimal shape which catches the sight of even the most difficult judge.
- No moving parts, only a small screen, the sensors and two LEDs. Suitable for playing games anywhere you are, provided you
have a wifi connection.
- Functionality is increased further by building and connecting the device to a custom tailored app, enabling it for future improvements
in terms of software.