from sh import human
import os
import machine
import time


def __main__(args):
	num = 1
	pin=2
	if len(args) > 2:
		pin = int(args[2])
	if len(args) > 3:
		num = int(args[3])

	print("set pin{} value{}".format(pin, num))
	led = machine.Pin(pin, machine.Pin.OUT)
	led.value(num)


