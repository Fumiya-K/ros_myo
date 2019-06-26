#! /usr/bin/env python
# -*- coding: utf-8 -*-

from gui_manager import Application
import threading
from Tkinter import *
import Tkinter
import rospy


if __name__ == "__main__":
    # rospy.init_node("main_proc")
    root = Tk()
    root.title("GUI")
    app = Application(master=root)
    app.mainloop()
    rospy.spin()