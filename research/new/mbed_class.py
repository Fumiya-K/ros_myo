#! /usr/bin/env python

from serial import Serial
from time import sleep

class Mbed:
    def __init__(self, portname, baud):
        # super().__init__(portname, baud)
        self.mbed = Serial(portname, baud)

    """
    def mbedWrite(self, cmd, farray):
        a = []
        for i in farray:
            a.append(int(i))
        # print(a)
        buf = [0xfe, 0xef, cmd, len(farray)] + a
        # [ser.write(i.to_bytes(1, byteorder='little')) for i in buf]
        self.flushInput()
        self.flushOutput()
        [self.write(chr(i)) for i in buf]
    """

    def mbedWrite(self, cmd, farray):
        a = []
        for i in farray:
            a.append(int(i))
        print(a)
        buf = [0xfe, 0xef, cmd, len(farray)] + a
        # [ser.write(i.to_bytes(1, byteorder='little')) for i in buf]
        self.mbed.flushInput()
        self.mbed.flushOutput()
        [self.mbed.write(chr(i)) for i in buf]

if __name__ == "__main__":
    mbed = Mbed("/dev/ttyACM0", 9600)
    for i in range(10):
        mbed.mbedWrite(0x0a, [100, 250, 10, 20, 10])
        sleep(1)