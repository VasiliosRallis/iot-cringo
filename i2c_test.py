""" need to:
        - adjust the thresholds
        - connect to internet
        - reconsider when to take measurements (consider the timings too)
        - change the rate of reading for the ambient light value and average
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

RESET_THR = 15000
NEXT_THR = 3000
N = 7

SLAVEADDR = 19

COMMANDREG = 0x80
PROXIMITYPARAMETERS = 0x82
LIGHTPARAMETERS = 0x84
LIGHTREG = 0x85
PROXREG = 0x87

def main():
    print('Connecting to network...')
    initNetwork()

    client = setupClient()

    Bingo = False
    #specify the pins for the i2c communnication with the peripherals and fequency used
    i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
    
    # wait until the user touches the proximity sensor
    # get the seed to start the random sequence
    light = bootstrap(i2c)
    random.seed(light)
    print('Seed: ' + str(light))

    # Start game
    print('Game ON')
    results = results_init()
    ctr = 0
    while Bingo != True:
        proximity = read_prox(i2c)
        if (proximity > NEXT_THR):
        #################################################### 
        # check from the server if there is a bingo
        client.check_msg()
        ####################################################  
            while True:
                # generate a new random number
                r = random.getrandbits(N)
                sample = int(r * pow(2,N-1)/90)

                # if ((results[sample] != 0) || (sample == 0)):
                if sample == 0 or sample > 90:
                    #ignore reading
                    print(str(sample) + ' is ignored. Generating another number')
                elif results[sample-1] != 0: 
                    print('Number ' + str(sample) + ' spotted again. Generating another number') # generate another random number
                else:
                    results[sample-1] = sample    
                    ctr = ctr + 1
                    print('Ctr: ' + str(ctr) + ' Sample: ' + str(results[sample-1]))
                    json_string = {'Seed': str(light), 'Counter': str(ctr), 'Sample': str(sample)}
                    send_data(client,json_string)
                    break

            if ctr == 90:
                Bingo = True
##################### FILL IN ##################### 
            # pass it forward to the network
            # wait for some time to avoid same package sent multiplie times
            time.sleep(1)
#################################################### 
def setupClient():
    client = MQTTClient(machine.unique_id(), '192.168.0.10') #New MQTT instance
    client.connect()
    # client.set_callback(callback_function()) #Callback function for reading from MQTT
    # client.subscribe("esys/cringo/results")

    return client

def initNetwork():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if =network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('EEERover','exhibition')
    #Keep trying until it connects to the network
    while not sta_if.isconnected():
        pass
    print('The connection was successfull')

def send_data(client,json_string): 
    data= json.dumps(json_string)
    client.publish('esys/cringo/samples', bytes(data, 'utf-8'))#send  data to broker

def results_init():
    lst = []
    for i in range(0,90):
        lst.append(0)
    return lst

def bootstrap(i2c):
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
            print('Starting game....')
            start = True
    
    time.sleep(1)
    light = read_ambient(i2c)
    # disable ambient light (bit 2) sensor
    i2c.writeto_mem(SLAVEADDR,COMMANDREG,b'\x03')
    return light

def read_ambient(i2c):
    # request an ambient light measurement
    data = i2c.readfrom_mem(SLAVEADDR,LIGHTREG,2)
    conv_data = convert(data)
    return conv_data

def read_prox(i2c):
    data = i2c.readfrom_mem(SLAVEADDR,PROXREG,2)
    conv_data = convert(data)
    return conv_data

def convert(bytes):
    (bytes,) = struct.unpack('>h', bytes)
    return bytes


if __name__ == '__main__':
    main()