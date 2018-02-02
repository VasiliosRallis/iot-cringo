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

START_THR = 15000
NEXT_THR = 3000
N = 7

SLAVEADDR = 19

COMMANDREG = 0x80
PROXIMITYRATE = 0x82
LIGHTSENSORRATE = 0x84
LIGHTREG = 0x85
PROXREG = 0x87

def main():
    Bingo = False
    #specify the pins for the i2c communnication with the peripherals and fequency used
    i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
    # wait until the user touches the proximity sensor to start the game
    bootstrap(i2c)
    print('Game has started')
    # get the seed for the random sequence
    light = read_ambient_on_demand(i2c)
    # start a random sequence
    random.seed(light)
    # access command register, enable self-timed measurements(bit 0), periodic proximity (bit 1) 
    i2c.writeto_mem(SLAVEADDR,COMMANDREG,b'\x03')
    # keep 

    results = results_init()

    while Bingo != True:
        proximity = read_prox(i2c)
        if (proximity > NEXT_THR): 
            while True:
                # generate a new random number
                r = random.getrandbits(N)
                sample = int(r * pow(2,N-1)/(90-1))

                if (results[sample] != 0) || (sample == 0):
                    print(str(sample) + 'Found again') # generate another random number
                else:
                    results[sample] = sample
                    print(results[sample])
                    break
##################### FILL IN ##################### 
            # pass it forward to the network
            # wait for some time to avoid same package sent multiplie times
            time.sleep(1)
#################################################### 
def results_init():
    lst = []
    for i in range(1,91):
        lst.append(0)
    return lst

def bootstrap(i2c):
    start = False
    # access command register, enable self-timed measurements(bit 0), periodic proximity (bit 1) 
    i2c.writeto_mem(SLAVEADDR,COMMANDREG,b'\x03')
    # access proximity rate register, increase rate to 30 samples/s
    i2c.writeto_mem(SLAVEADDR,PROXIMITYRATE,b'\x04')
    # take readings until someone touches the proximity sensor
    while start!=True:
        proximity = read_prox(i2c)
        print(proximity)
        if proximity > START_THR:
            start = True

def read_ambient_on_demand(i2c):
    # request an ambient light measurement
    time.sleep(0.1)
    i2c.writeto_mem(SLAVEADDR,COMMANDREG,b'\x10')
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