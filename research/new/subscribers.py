#! /usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from ros_myo.msg import EmgArray
from std_msgs.msg import Float32
import serial

class EmgSubscribers():
    def __init__(self):
        self.subscriber = rospy.Subscriber('/myo_raw/myo_emg', EmgArray, self.callback)
        self.message = EmgArray
        self.EMG = [0 for i in range(8)]
        self.count1 = 0
        self.count2 = 0
        self.buf = [0 for i in range(8)]
        self.emgs = [0 for i in range(8)]
        self.measurement_n = 50
        self.pr = 1.2
    
    def callback(self, message):
        self.emgs = message.data
        for i in range(len(self.emgs)):
            self.buf[i] += self.emgs[i]
        self.count1 += 1
        if self.count1 == self.measurement_n:
            for i in range(len(self.buf)):
                self.EMG[i] = self.buf[i] / self.measurement_n
            self.count1 = 0
            self.buf = [0 for i in range(8)]


class PoseSubscribers():
    def __init__(self, portname, baud):
        self.subscriber = rospy.Subscriber("/roll_deg", Float32, self.callback)
        self.ser = serial.Serial(portname, baud)
    
    def callback(self, msg):
        deg = int(msg.data * 180 / 3.1415926535)
        self.serialWrite(0x0b, [deg])

    def serialWrite(self, cmd, farray):
        a = []
        for i in farray:
            a.append(int(i))
        # print(a)
        buf = [0xfe, 0xef, cmd, len(farray)] + a
        # [ser.write(i.to_bytes(1, byteorder='little')) for i in buf]
        if connected:
            self.ser.flushInput()
            self.ser.flushOutput()
            [self.ser.write(chr(i)) for i in buf]