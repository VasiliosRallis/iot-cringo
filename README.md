# Embedded_coursework_1
## IOT coursework - Cringo device

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

## IOT coursework - Cringo App version 1.0

- Cringo Android App is an android application which in combination with the cringo device replace the traditional game bingo.
- Random numbers generated from the device are published to the MQTT broker. Our app subscribes to this topic in order to receive the published data.
- In addition, our app provides a BINGO  button to send an identification that a bingo event occurs. The message is sent to a topic where our Cringo device subscribes.
- All the message are encrypted to JSON format to ensure a safe and efficient transmission of data between app, broker and device.
- Buttons to connect and disconnect to the broker are also implemented, to enable the user to enter and exit the game at any time.
- Further functionalities are to be implemented in newer versions of app.

## Build Configuration
This project was build on JDK 1.6

## License
Copyrights 2018 included. In Chris We Trust Ltd.
