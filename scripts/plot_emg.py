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
        self.RP = realtime_plot()
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
    def __init__(self):
        self.fig = plt.figure(figsize=(15, 15))
        self.initialize()

    def initialize(self):
        self.fig.suptitle('EMG', size=15)
        plt.subplots_adjust(wspace=0.4, hspace=1.0)
        self.ax0 = plt.subplot2grid((8, 1),(0,0))
        self.ax1 = plt.subplot2grid((8, 1),(1,0))
        self.ax2 = plt.subplot2grid((8, 1),(2,0))
        self.ax3 = plt.subplot2grid((8, 1),(3,0))
        self.ax4 = plt.subplot2grid((8, 1),(4,0))
        self.ax5 = plt.subplot2grid((8, 1),(5,0))
        self.ax6 = plt.subplot2grid((8, 1),(6,0))
        self.ax7 = plt.subplot2grid((8, 1),(7,0))
        self.ax0.grid(True)
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.ax3.grid(True)
        self.ax4.grid(True)
        self.ax5.grid(True)
        self.ax6.grid(True)
        self.ax7.grid(True)
        self.ax0.set_title('ch0')
        self.ax1.set_title('ch1')
        self.ax2.set_title('ch2')
        self.ax3.set_title('ch3')
        self.ax4.set_title('ch4')
        self.ax5.set_title('ch5')
        self.ax6.set_title('ch6')
        self.ax7.set_title('ch7')
        
        self.ax0.set_ylim((0, 1100))
        self.ax1.set_ylim((0, 1100))
        self.ax2.set_ylim((0, 1100))
        self.ax3.set_ylim((0, 1100))
        self.ax4.set_ylim((0, 1100))
        self.ax5.set_ylim((0, 1100))
        self.ax6.set_ylim((0, 1100))
        self.ax7.set_ylim((0, 1100))
        t = np.arange(4, 0., -4./200.)
        self.ax0.set_xlim((t.min(), t.max()))
        self.ax1.set_xlim((t.min(), t.max()))
        self.ax2.set_xlim((t.min(), t.max()))
        self.ax3.set_xlim((t.min(), t.max()))
        self.ax4.set_xlim((t.min(), t.max()))
        self.ax5.set_xlim((t.min(), t.max()))
        self.ax6.set_xlim((t.min(), t.max()))
        self.ax7.set_xlim((t.min(), t.max()))

        # プロットの初期化
        self.lines0, = self.ax0.plot([-1, -1], [1, 1])
        self.lines1, = self.ax1.plot([-1, -1], [1, 1])
        self.lines2, = self.ax2.plot([-1, -1], [1, 1])
        self.lines3, = self.ax3.plot([-1, -1], [1, 1])
        self.lines4, = self.ax4.plot([-1, -1], [1, 1])
        self.lines5, = self.ax5.plot([-1, -1], [1, 1])
        self.lines6, = self.ax6.plot([-1, -1], [1, 1])
        self.lines7, = self.ax7.plot([-1, -1], [1, 1])
        
    def set_data(self, data):
        t = np.arange(4, 0., -4./200.)
        self.lines0.set_data(t, data[0])
        self.lines1.set_data(t, data[1])
        self.lines2.set_data(t, data[2])
        self.lines3.set_data(t, data[3])
        self.lines4.set_data(t, data[4])
        self.lines5.set_data(t, data[5])
        self.lines6.set_data(t, data[6])
        self.lines7.set_data(t, data[7])

    def pause(self,second):
        while(True):
            # self.t += 4./200.
            plt.pause(second)


if __name__ == "__main__":
    rospy.init_node("plots_emg")
    sub = EmgSubscriber()
    rospy.spin()