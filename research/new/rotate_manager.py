#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import PoseStamped, Quaternion
from std_msgs.msg import UInt8, Float32, Int16MultiArray
from copy import deepcopy
from tf.transformations import *

class PoseTransformer():
    def __init__(self):
        self.subscriber = rospy.Subscriber("/myo_raw/pose", PoseStamped, self.callback)
        self.sw_sub = rospy.Subscriber("init_pose", UInt8, self.init_pose)
        self.rotate_pub = rospy.Publisher("/forearm", PoseStamped, queue_size=1)
        self.adjusted_pub = rospy.Publisher("/adjusted_pose", PoseStamped, queue_size=1)
        self.adjusted_pub4mbed = rospy.Publisher("/adjusted_pose4mbed", Int16MultiArray, queue_size=1)
        # self.roll_pub = rospy.Publisher("/roll_deg", Float32, queue_size=1)
        # self.init_trigger = rospy.Subscriber("init_trigger", UInt8, self.init_pose)
        self.current_q = Quaternion(0., 0., 0., 0.)
        self.first_q = Quaternion(1., 1., 1., 1.)
        self.initialized = False
        self.topic_roll = PoseStamped()
        self.topic_adjust = PoseStamped()
        self.topic_adjust_rpy = Int16MultiArray()
        self.topic_roll.header.frame_id = "myo_raw"
        self.topic_adjust.header.frame_id = "myo_raw"
        self.flg = False


    def init_pose(self, msg):
        self.first_q = deepcopy(self.current_q)
        self.flg = True


    def callback(self, msg):
        quat = msg.pose.orientation
        self.current_q = Quaternion(quat.x, quat.y, quat.z, quat.w)
        # q_first is first quaternion
        # q_now is current quaternion
        # q_roll is goal quaternion

        q_first = [self.first_q.x, self.first_q.y, self.first_q.z, -self.first_q.w]
        q_now = [quat.x, quat.y, quat.z, quat.w]
        q_adjust = quaternion_multiply(q_now, q_first)
        q_roll = quaternion_from_euler(list(euler_from_quaternion(q_adjust))[2], 0, 0)

        self.topic_adjust.pose.orientation = Quaternion(q_adjust[0], q_adjust[1], q_adjust[2], q_adjust[3])
        self.adjusted_pub.publish(self.topic_adjust)
        self.topic_roll.pose.orientation = Quaternion(q_roll[0], q_roll[1], q_roll[2], q_roll[3])
        self.rotate_pub.publish(self.topic_roll)
        if self.flg:
            self.topic_adjust_rpy.data = [i * 180 / math.pi for i in list(euler_from_quaternion(q_adjust))]
            self.adjusted_pub4mbed.publish(self.topic_adjust_rpy)


if __name__ == "__main__":
    rospy.init_node("rotate_manager")
    sub = PoseTransformer()
    rospy.spin()