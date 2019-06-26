#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3, PoseStamped
from time import time
from tf.transformations import *
from math import sin, cos
import numpy as np

class Travel_calc():
    def __init__(self):
        self.imu_sub = rospy.Subscriber("/myo_raw/myo_imu", Imu, self.sensor2abs)
        self.adjusted_sub = rospy.Subscriber("/adjusted_pose", PoseStamped, self.update_pose)
        self.acc_abs_pub = rospy.Publisher("/acc_abs", Vector3, queue_size=1)
        self.pose = [0., 0., 0.]

    def sensor2abs(self, msg):
        acc = msg.linear_acceleration
        acc_v = np.array([acc.x, acc.y, acc.z])
        acc_abs = np.dot(rotate_matrix(self.pose), acc_v)
        self.acc_abs_pub.publish(Vector3(acc_abs[0], acc_abs[1], acc_abs[2]))

    def update_pose(self, msg):
        quat = msg.pose.orientation
        self.pose = list(euler_from_quaternion([quat.x, quat.y, quat.z, quat.w]))

# theta = [theta_r, theta_p, theta_y]
def rotate_matrix(euler):
    sr = sin(euler[0])
    sp = sin(euler[1])
    sy = sin(euler[2])
    cr = cos(euler[0])
    cp = cos(euler[1])
    cy = cos(euler[2])
    Rx = np.array([[1, 0, 0],
                   [0, cr, sr],
                   [0, -sr, cr]])
    Ry = np.array([[cp, 0, -sp],
                   [0, 1, 0],
                   [sp, 0, cp]])
    Rz = np.array([[cy, sy, 0],
                   [-sy, cy, 0],
                   [0, 0, 1]])
    R = np.dot(Rz, np.dot(Ry, Rx))
    return R


if __name__ == "__main__":
    rospy.init_node("travel_calc")
    T = Travel_calc()
    rospy.spin()