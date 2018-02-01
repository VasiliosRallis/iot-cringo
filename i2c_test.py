import machine
from machine import I2C, Pin

print("Starting I2C")
#specify the pins for the i2c communnication with the peripherals and fequency used
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

i2c.scan()
# access command register, enable self-timed measurements(bit 0), periodic proximity (bit 1) 
# and als (bit 2) measurement
i2c.writeto_mem(19,0x80,bytearray([0x7])

# access rate of proximity measurement, default 0x0
#i2c.writeto_mem(19,0x82,bytearray([0x1])

# access ID LED (bits 0-5) current register to set LED current value for proximity measurement
# IR LED current = Value * 10mA
#i2c.writeto_mem(19,0x83,bytearray([0x1])

# access Ambient Light Parameter Register
#i2c.writeto_mem(19,0x84,bytearray([0x11])
i2c.readfrom_mem(19,0x85,1)
i2c.readfrom_mem(19,0x86,1)