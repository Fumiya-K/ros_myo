#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import Imu
import matplotlib.pyplot as plt
import numpy as np

angle = Vector3
Initialized = False
init_angle = Vector3

# "p" is eular angle array
def rotM(angle):
	px = angle.x - init_angle.x
	py = angle.y - init_angle.y
	pz = angle.z - init_angle.z

	Rx = np.array([[1, 0, 0],
                   [0, np.cos(px), np.sin(px)],
                   [0, -np.sin(px), np.cos(px)]])
	Ry = np.array([[np.cos(py), 0, -np.sin(py)],
                   [0, 1, 0],
                   [np.sin(py), 0, np.cos(py)]])
	Rz = np.array([[np.cos(pz), np.sin(pz), 0],
                   [-np.sin(pz), np.cos(pz), 0],
                   [0, 0, 1]])
	R = Rz.dot(Ry).dot(Rx)

	return R


def callback(msg):
	global angle
	buf = msg.linear_acceleration
	acc = np.array([buf.x, buf.y, buf.z])
	R = rotM(angle)
	abs_acc = np.dot(R, acc)
	print(abs_acc)


def setAngle(msg):
	global angle, Initialized, init_angle
	if not Initialized:
		Initialized = True
		init_angle = msg
	angle = msg


if __name__ == "__main__":
	rospy.init_node("my_pos_estimate")
	ori_sub = rospy.Subscriber("/myo_raw/myo_ori", Vector3, setAngle)
	imu_sub = rospy.Subscriber("/myo_raw/myo_imu", Imu, callback)
	rospy.spin()
