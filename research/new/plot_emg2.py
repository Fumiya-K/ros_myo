#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import rospy
from ros_myo.msg import EmgArray
import matplotlib.pyplot as plt
import threading as th
from copy import deepcopy

class EmgSubscriber():
    def __init__(self):
        n_ch = 8
        self.RP = realtime_plot(n_ch)
        self.subscriber = rospy.Subscriber("/myo_raw/myo_emg", EmgArray, self.callback)
        self.Emgs = np.zeros((8, 200))
        self.th1 = th.Thread(target=(self.RP.pause(4./200.)))
        self.th1.start()
    
    def callback(self, msg):
        get_emg = msg.data
        for i in range(len(get_emg)):
            buf = np.delete(self.Emgs[i], -1)
            self.Emgs[i] = np.insert(buf, 0, get_emg[i])
        self.RP.set_data(self.Emgs)
            
class realtime_plot(object):
    def __init__(self, num):
        self.fig = plt.figure(figsize=(15, 15))
        self.n_ch = num
        self.initialize()

    def initialize(self):
        self.fig.suptitle('EMG', size=15)
        plt.subplots_adjust(wspace=0.4, hspace=1.0)
        t = np.arange(4, 0., -4./200.)
        self.axs = [plt.subplot2grid((self.n_ch, 1),(i,0)) for i in range(self.n_ch)]
        self.lines = [None for i in range(self.n_ch)]
        for i in range(self.n_ch):
            self.axs[i].grid(True)
            self.axs[i].set_title("ch{}".format(i+1))
            self.axs[i].set_ylim((0, 1100))
            self.axs[i].set_xlim((t.min(), t.max()))
            self.lines[i], = self.axs[i].plot([-1, 1], [1, 1])

    def set_data(self, data):
        t = np.arange(4, 0., -4./200.)
        for i in range(self.n_ch):
            self.lines[i].set_data(t, data[i])

    def pause(self,second):
        while(True):
            # self.t += 4./200.
            plt.pause(second)


if __name__ == "__main__":
    rospy.init_node("plots_emg")
    sub = EmgSubscriber()
    rospy.spin()