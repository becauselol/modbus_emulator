import minimalmodbus
import serial
import time
import datetime
import sys

for i in range(1, 248):
    try:
        instrument = minimalmodbus.Instrument('/dev/ttyUSB0', i)
        instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
        instrument.serial.baudrate = 9600
        instrument.serial.stopbits = 1

        value = instrument.read_float(50, number_of_registers=2)
        print(i)
        print(value)
    except:
        print("fail")
        pass
