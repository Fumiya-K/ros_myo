#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Quaternion, PoseStamped, Vector3
from sensor_msgs.msg import Imu
from tf.transformations import *

class PositionEstimate():
    def __init__(self):
        self.quat_angl_sub = rospy.Subscriber("/adjusted_pose", PoseStamped, self.update_angl)
        self.imu_sub = rospy.Subscriber("/myo_raw/myo_imu", Imu, self.position_estimate)
        self.pub = rospy.Publisher("/acc", Vector3, queue_size=1)
        self.angl = [0, 0, 0, 0]

    def update_angl(self, msg):
        quat = msg.pose.orientation
        self.angl = [quat.x, quat.y, quat.z, quat.w]

    def position_estimate(self, msg):
        acc = msg.linear_acceleration
        acc_q = [acc.x, acc.y, acc.z, 0]
        angl_i = [self.angl[0], self.angl[1], self.angl[2], -self.angl[3]]
        acc_abs = quaternion_multiply(quaternion_multiply(angl_i, acc_q), self.angl)
        self.pub.publish(Vector3(acc_abs[0], acc_abs[1], acc_abs[2]))

if __name__ == "__main__":
    rospy.init_node("PositionEstimater")
    pe = PositionEstimate()
    rospy.spin()