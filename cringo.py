"""
- Micropython code for Cringo device.
"""
import machine
import time
import math
import array
import ustruct as struct
import urandom as random
from machine import I2C, Pin
import ujson as json
from umqtt.simple import MQTTClient
import network
import ssd1306      # library provided from micropython for the OLED Display

RESET_THR = 15000   # Threshold of proximity sensor to reset the game
NEXT_THR = 7000     # Threshold of proximity sensor to request new number
N = 7               # Number of bits of the generated number

SLAVEADDR = 19      # Address of the sensor used by the i2c
OLEDADDR = 61       # Address of the OLED display used by the i2c

# Addresses for various registers of the ambient light and proximity sensor
COMMANDREG = 0x80           # Address of the command register
PROXIMITYPARAMETERS = 0x82  # Address of the parameters register of proximity sensor
LIGHTPARAMETERS = 0x84      # Address of the parameters register of ambient light sensor
LIGHTREG = 0x85             # Address of the data register of the ambient light sensor
PROXREG = 0x87              # Address of the data register of the proximity sensor

BINGO = False   # Used as flag to indicate if a bingo has occured

"""
    Main function. 
        Sets up the device(communications, network, screen)
        Sets up the game(enables the sensors, seeds the RNG and prints on screen info about the game)
        Starts a bingo session
        After the session is finished, displays on screen that bingo has occured and that the game has ended
        Restarts the game on demand
"""
def main():
    (i2c, client, oled) = dev_setup()   # Sets up the device

    while True:
        (light, results, ctr, oled) = game_setup(i2c, oled)
        bingo_game(i2c, client, light, ctr, results, oled)  # Start a bingo session
        print_screen(oled)  # Print on OLED screen bingo and instructions on how to start new game                               
        client.disconnect() # Disconnects the client to release resources
                            # and avoid reading multiple bingo requests
        while True:    
            time.sleep(2)                   # Waits for 2secs
            if read_prox(i2c)>RESET_THR:    # If the proximity sensor is still being touched, starts a new game
                global BINGO
                BINGO = False           # Reset the flag
                client = setupClient()  # Sets up a new client for the new game
                break
"""
    Device setup function
        Specifies the i2c communication with the peripherals
        Initialises the OLED display
        Connects the device to the wifi network
        And sets up the MQTT broker for internet communication
"""
def dev_setup():
    i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)  # Specify the pins for the i2c communnication 
                                                    # with the peripherals and fequency used
    oled = initialise_OLED(i2c)                     # Resets and connects to the OLED display  
    # Erases the screen and prints info about network connection
    oled.fill(0)                                    
    oled.text('Connecting to ', 0, 0)
    oled.text('network...',0,10)
    oled.show()
    initNetwork(oled)                   # Connects to the wifi network
    # Guides the user how to move forward via printing info on screen
    oled.text('Touch to move',5,30)     
    oled.text('forward',30,40)
    oled.show()
    client = setupClient()              # Sets up MQTT broker
    return (i2c, client, oled)

def initialise_OLED(i2c):
    reset = machine.Pin(16, machine.Pin.OUT, None)  # Resets the OLED display
    reset.value(0)
    # Wait for reset to complete
    time.sleep_ms(200)
    # Turn off reset
    reset.value(1)
    # Connects to the screen via i2c
    oled = ssd1306.SSD1306_I2C(128, 64, i2c,OLEDADDR)   # Resolution: 128x64
    oled.text('Cringo',35,22)
    oled.text('Time',42,32)
    oled.show()
    time.sleep(1)
    return oled

def initNetwork(oled):
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if =network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('EEERover','exhibition')
    #Keep trying until it connects to the network
    while not sta_if.isconnected():
        pass
    oled.text('Connected!', 0, 20)
    oled.show()
    time.sleep_ms(250)
"""
    MQTT broker setup function
        Creates a new MQTT instance and connects to the server
        Also subscribes to the right topic to read data from the server
"""
def setupClient():
    client = MQTTClient(machine.unique_id(), '192.168.0.10') #New MQTT instance
    client.connect()
    client.set_callback(callback_function) #Callback function for reading from MQTT
    client.subscribe("esys/cringo/samples/subscribe")

    return client
"""
    Callback function 
        Performed when a message is received from the server
        When a message is published in the topic where the device is subscribed
        a certain action is performed by the function
"""
def callback_function(topic, data):
    received_dict = json.loads(data)    # Creates a dictionary from the received json message

    if topic == b'esys/cringo/samples/subscribe':   # if the message is from a subscribed topic
        if received_dict['bingo'] == "1":           # indicating the the bingo field is
            global BINGO                            # bingo has occured so the BINGO flag is raised
            BINGO = True
"""
    Game setup function
        Initialises the game
        Takes a reading from the ambient light sensor and uses it to seed the RNG
        Prints on screen the seed and initialises the results array
"""
def game_setup(i2c, oled):
    # wait until the user touches the proximity sensor
    # get the seed to start the random sequence
    (light) = bootstrap(i2c,oled)   # Enables the proximity and ambient light sensors and returns a reading from the ambient light sensor
    random.seed(light)              # The ambient light reading is used as a random seed to initialise the generator
    oled.text('Seed: ' + str(light), 0,10)
    oled.text('Touch to start',5,30)
    oled.text('the game',25,40)
    oled.show()
    # time.sleep(2)    
    results = results_init()    # Array of 90 locations to accomodate the generated numbers
    ctr = 0                     # Measures the number of samples stored in the array.
    return (light,results,ctr, oled)
"""
    bootstrap function
        Enables the sensors via the command register
        Changes the parameters of each to take more samples than the default
        Checks if someone tries to touch the proximity sensor and if so the game starts by taking 
        a reading from the ambient light sensor. After the reading is taken, the ambient light sensor is disabled to save power
"""
def bootstrap(i2c,oled):
    start = False
    # access command register, enable self-timed measurements(bit 0), periodic proximity (bit 1) and ambient light (bit 2) 
    i2c.writeto_mem(SLAVEADDR,COMMANDREG,b'\x07')
    # access proximity rate register, increase rate to 30 samples/s
    i2c.writeto_mem(SLAVEADDR,PROXIMITYPARAMETERS,b'\x04')
    # set ambient light sensor to continuous conversion mode taking 10 samples/s and averaging them
    i2c.writeto_mem(SLAVEADDR,LIGHTPARAMETERS,b'\xF7')
    
    # take readings until someone touches the proximity sensor
    while start!=True:
        proximity = read_prox(i2c)
        # print(proximity)
        if proximity > NEXT_THR:
            oled.fill(0)
            oled.text('Game starts...',0,0)
            oled.show()
            # print('Starting game....')
            start = True
    
    time.sleep(1)
    # take a reading from the ambient light sensor
    light = read_ambient(i2c)
    # disable ambient light (bit 2) sensor
    i2c.writeto_mem(SLAVEADDR,COMMANDREG,b'\x03')
    return (light)
"""
    List Initialisation function
        Creates a list of 90 samples all initialised to zero.
        This is to accomodate the generated numbers of the game
"""
def results_init():
    lst = []
    for i in range(0,90):
        lst.append(0)
    return lst
"""
    Bingo Game function
        A single bingo game.
        A proximity reading is taken to check if the user has requested another number
        After every request check if there are new messages from the server to check if a BINGO has occured
        If there is no BINGO, a new random number is generated and it is mapped in the range of 1 to 90
        This number is stored in the results list if it has not already stored in there. If it has, another sample is generated
        The number then is printed on the OLED display and also is sent to the MQTT broker as a JSON formatted message along with
        the seed and the counter

"""
def bingo_game(i2c, client, light, ctr, results, oled):
    while BINGO != True:
        proximity = read_prox(i2c)  # Take a proximity reading
        if (proximity > NEXT_THR):
            # check from the server if there is a bingo
            client.check_msg()

            if BINGO == False:
                while True:
                    # generate a new random number
                    r = random.getrandbits(N)
                    sample = int(r * pow(2,N-1)/90) # Map the generated number in the range of 1 to 90

                    if sample == 0 or sample > 90: # If for some reason, number is out of range
                        #ignore reading
                        print(str(sample) + ' is ignored. Generating another number')
                    elif results[sample-1] != 0:    # If the number already exists in the list ignore it
                        print('Number ' + str(sample) + ' spotted again. Generating another number') # generate another random number
                    else:
                        results[sample-1] = sample  # use the sample as the index of the array too (use -1 to compensaty for the zero indexing)   
                        ctr = ctr + 1   # increase the counter by one
                        oled.fill(0)
                        oled.text(str(sample), 50, 30)  # Print the number on the screen
                        oled.show()
                        json_string = {'Seed': str(light), 'Counter': str(ctr), 'Sample': str(sample)}  # Create the JSON message
                        send_data(client,json_string)   # Send the message to the server through the MQTT broker
                        json_string= sample
                        send_to_app(client,json_string)
                        break

                time.sleep(1)

def send_data(client,json_string): 
    data= json.dumps(json_string) # Converts the message into JSON format
    client.publish('esys/cringo/samples/server', bytes(data, 'utf-8'))  # Sends data to broker

def send_to_app(client,json_string):
    data= json.dumps(json_string) # Converts the message into JSON format
    client.publish('esys/cringo/samples/publish', bytes(data, 'utf-8'))# Send data to broker

def read_ambient(i2c):
    # request an ambient light measurement
    data = i2c.readfrom_mem(SLAVEADDR,LIGHTREG,2)
    conv_data = convert(data)
    return conv_data

def read_prox(i2c):
    data = i2c.readfrom_mem(SLAVEADDR,PROXREG,2)
    conv_data = convert(data)   # might change it to int.from_bytes(data,'big')
    return conv_data

def convert(bytes):
    (bytes,) = struct.unpack('>h', bytes)
    return bytes

def print_screen(oled):
    # flash BINGO!! when the game ends
    for i in range(0,6):
        oled.fill(0)
        oled.show()
        time.sleep_ms(500)
        oled.text('BINGO!!',35,30)
        oled.show()
        time.sleep_ms(500)

    oled.fill(0)
    oled.text('Game has ended.', 3,20)
    oled.text('Long touch to',7,30)
    oled.text('start a new one',0,40)
    oled.show()

if __name__ == '__main__':
    main()