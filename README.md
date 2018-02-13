# embedded_cw1
IOT coursework

IOT coursework - Cringo App version 1.0

- Cringo Android App is an android application which in combination with the cringo device replace the traditional game bingo.

- Random numbers generated from the devices are published to the MQTT broker. Our app subscribes to this topic in order to receive the published data.

- In addition, our app provides a BINGO  button to send an identification that a bingo event occurs. The message is sent to a topic where our Cringo device subscribes.

- All the message are encrypted to JSON format to ensure the safe and efficient transmission of data between app, broker and device.

- Button to connect and disconnect to the broker are also implemented to enable the user to enter and exit the game at any time.

- Further functionalities are to be implemented in newer versions of app.
