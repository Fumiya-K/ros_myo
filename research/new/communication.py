#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import PoseStamped, Quaternion
from std_msgs.msg import UInt8MultiArray
from mbed_class import Mbed
from tf.transformations import euler_from_quaternion
from math import pi

PORTNAME = "/dev/ttyACM1"
BAUD = 115200

class Communication():
    def __init__(self, mbed):
        self.mbed = mbed
        self.finger_state_sub = rospy.Subscriber("/finger_state", UInt8MultiArray, self.finger)
        self.pose_sub = rospy.Subcriber("/adjusted_pose", PoseStamped, self.pose)
        self.cmd = {"finger":0x0a, "pose":0x0b}


    def finger(self, msg):
        self.mbed.mbedWrite(cmd["finger"], msg.data)

    
    def pose(self, msg):
        rpy = list(euler_from_quaternion(msg.pose.orientation))
        def rad2deg(arr):
            return [i * 180 / pi for i in arr]
        rospy.loginfo(rad2deg(rpy))
        self.mbed.mbedWrite(cmd["pose"], rad2deg(rpy))



if __name__ == "__main__":
    rospy.init_node("Communication")
    try:
        sub = Communication(Mbed(PORTNAME, BAUD))
    except serial.serialutil.SerialException:
        pass
    rospy.spin()