#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import Imu
import numpy as np


c_imu, c_angle = 0, 0

def cb_imu(msg):
	global c_imu
	c_imu += 1

def cb_angle(msg):
	global c_angle
	c_angle += 1
	if c_angle == 400:
		print("count of received data of angle = {}".format(c_angle))
		print("count of received data of imu = {}".format(c_imu))

if __name__ == "__main__":
	rospy.init_node("freq_checker")
	imu_sub = rospy.Subscriber("/myo_raw/myo_ori", Vector3, cb_angle)
	ang_sub = rospy.Subscriber("/myo_raw/myo_imu", Imu, cb_imu)

	rospy.spin()
