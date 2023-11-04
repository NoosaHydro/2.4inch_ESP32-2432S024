from sh import human
import os
import machine
import time
import struct

i2c = machine.SoftI2C(scl=machine.Pin(32), sda=machine.Pin(33), freq=400000)
i2c.writeto_mem(21, 0xfe, b'\xff') # tell it not to sleep


def __main__(args):
        #num = 10
        #pin=2
        #if len(args) > 2:
        #       pin = int(args[2])

        #print("blink pin{} ondelay{} offdelay{} loop{}".format(pin, ton, toff, num))

    while True:
        index, gesture, x, y = struct.unpack('>BBHH',i2c.readfrom_mem(21, 0x01, 6)) # see https://docs.python.org/3/library/struct.html
        xb = x & 0xFFF
        yb = y & 0xFFF
        #data = i2c.readfrom_mem(15, 0x01, 6)
        #print(data)
        print(index, gesture, x, y,xb,yb)
        time.sleep(0.1)
