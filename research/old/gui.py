#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import Tkinter
import Similarity
import numpy as np
import rospy, math
from std_msgs.msg import UInt8, String
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist, Vector3
from ros_myo.msg import EmgArray
import threading as th
from copy import deepcopy
import ttk, time, fcntl, termios, sys, os
import serial
# ----------------------------------- class -------------------------------------- #
class Subscribers():
    def __init__(self):
        self.subscriber = rospy.Subscriber('/myo_raw/myo_emg', EmgArray, self.callback)
        self.message = EmgArray
        self.EMG = [0 for i in range(8)]
        self.count1 = 0
        self.count2 = 0
        self.buf = [0 for i in range(8)]
        self.emgs = [0 for i in range(8)]
        self.measurement_n = 50
    
    def callback(self, message):
        self.emgs = message.data
        for i in range(len(self.emgs)):
            self.buf[i] += self.emgs[i]
        self.count1 += 1
        if self.count1 == self.measurement_n:
            for i in range(len(self.buf)):
                sub.EMG[i] = self.buf[i] / self.measurement_n
            self.count1 = 0
            self.buf = [0 for i in range(8)]
            # print(sim.Values)
            # print(sim.Simiraly)

# ---------------------------------- functions ------------------------------------ #
def button1_click():
    if sub.EMG == None:
        return
    if tb1.get() == tb_defalt:
        tb2_print("Please input pose name")
    else:
        countdown(2)
        sim.Add(deepcopy(sub.EMG))
        Posenames.append(tb1.get())
        finger_state.append([0, 0, 0, 0, 0, 0])
        lb.insert(END, tb1.get())

        
        cb['values'] = Posenames
        tb1_clear()

def button2_click():
    if cb.current() >= 0:
        Posenames.pop(cb.current())
        finger_state.pop(cb.current())
        sim.Delete(cb.current())
        cb['values'] = Posenames
        lb_update()

def button3_click():
    global st_flg
    st_flg = not st_flg

def button4_click():
    global finger_state
    if tb1.get() == tb_defalt or cb.current == -1:
        tb2_print("Please input finger state")
        tb2_print("ex) 1 1 0 1 1 1 ")
    else:
        arr = tb1.get().split()
        print(arr)
        finger_state[cb.current()] = arr

def find_proc():
    sub_win = Toplevel()
    var = StringVar()
    l = Label(sub_win, textvariable=var, font=("Helvetica", "96", "bold"))
    l.pack()
    while True:
        pre_ind = -1
        while st_flg:
            ind, coef = sim.Find(sub.emgs)
            # print(ind, coef)
            if coef >= Min:
                if ind != pre_ind:
                    tb2.delete("1.0", "end")
                    tb2.insert(END, "\n {} coef = {}".format(Posenames[ind], round(coef, 4)))
                    var.set(Posenames[ind])
                    pre_ind = ind
                    serialWrite(finger_state[ind])

def change_threshold(*args):
    global Min
    Min = float(s1.get()) / 100
    tb2_print("Min = {}".format(Min))

def change_mesurement_n(*args):
    sim.measurement_n = s2.get()
    tb2_print("Mesurement Numeber = {}".format(sim.measurement_n))

def tb1_clear():
    tb1.delete(0, Tkinter.END)
    tb1.insert(Tkinter.END, tb_defalt)

def tb2_print(s):
    tb2.insert(END, "\n{}".format(s))
    tb2.see("end")

def countdown(t):
    for i in range(t):
        time.sleep(1)

def lb_update():
    lb.delete(0, END)
    for i in Posenames:
        lb.insert(END, i)

def save_param():
    global file_name
    if tb1.get() == tb_defalt:
        print("Please input file name.")
    else:
        file_name = tb1.get()
        np.savez(file_name + ".npz", x=np.array(Posenames), y=np.array(finger_state))
        sim.Save(file_name)
        tb1_clear()
        tb2_print("Complete")

def load_param():
    global file_name, Posenames, finger_state
    if tb1.get() == tb_defalt:
            print("Please input file name.")
    else:
        file_name = tb1.get()
        zp = np.load(file_name+".npz")
        Posenames = zp["x"].tolist()
        finger_state = zp["y"].tolist()
        # print(finger_state)
        sim.Load(file_name)
        cb['values'] = Posenames
        lb_update()
        tb1_clear()
        tb2_print("Loaded")

def serialWrite(farray):
    a = []
    for i in farray:
        a.append(int(i))
    # print(a)
    buf = [0xfe, 0xef, len(farray)] + a
    # [ser.write(i.to_bytes(1, byteorder='little')) for i in buf]
    if connected:
        ser.flushInput()
        ser.flushOutput()
        [ser.write(chr(i)) for i in buf]

def sum_str(str_arr):
    string = ""
    for i in str_arr:
        string += i
    return string

# ----------------------------------- Valiables ----------------------------------- #
sub = Subscribers()
sim = Similarity.Similarity()
Posenames = []
finger_state = []
root = Tk()
Min = 0.95
tb_defalt = "new pose name or filename to load and save"
th1 = th.Thread(target=find_proc)
st_flg = False
file_path = "/home/fumyia/"
portname = "/dev/ttyACM1"
baudrate = 115200
connected = False
try:
    ser = serial.Serial(portname, baudrate)
    connected = True
    print("Mbed is connected")
except serial.serialutil.SerialException:
    connected = False

explanations = []
explanations.append("1. ポーズの登録\n・TextBoxに登録したいポーズの名前を入力\n・Addボタンを押し、手を登録したいポーズにする\n・テキストボックスに結果が表示されれば登録完了。ComboBoxに登録したポーズが追加される\n\n")
explanations.append("2. ポーズの削除\n・現状、Editボタンが機能しないため、教師データを変更したい場合は削除する必要がある\n・ComboBoxから削除したいポーズを選択する\n・Deleteボタンを押し、削除する\n\n")
explanations.append("3. ロボットハンドの状態\n・ComboBoxから設定したいポーズの名前を選択する\n・親指の回内外, 親指の屈曲, 人差し指の屈曲, 中指の屈曲, 薬指の屈曲, 小指の屈曲\n・上の順に曲げるなら1, そうでない場合は0を入力する\n・例）1, 1, 1, 0, 1, 1 \n\n")
explanations.append("4. ポーズ判定の実行\n・Find/Stopボタンを押すとポーズ判別が開始する\n・判定を終了したい場合は同様にFind/Stopボタンを押す\n\n")
explanations.append("5. セーブとロード\n・テキストボックスにセーブ(ロード)したいファイル名を入力し、Save(Load)ボタンを押す\n\n")
explanation = sum_str(explanations)
# ------------------------------------ Widgets ------------------------------------ #
root.title("Pose Estimation")
#root.geometry("400x300")
button1 = Button(root, text="Add", command=button1_click, height=2, width=5) # button2
button2 = Button(root, text="Delete", command=button2_click, height=2, width=5) # button3
button3 = Button(root, text="Find/Stop", command=button3_click, height=2, width=5)
button4 = Button(root, text="Edit", command=button4_click, height=2, width=5)
button5 = Button(root, text="Save", command=save_param, height=2, width=5)
button6 = Button(root, text="Load", command=load_param, height=2, width=5)
# button6 = Button(root, text="", command=, height=2, width=5)
cb = ttk.Combobox(root)
label_th = Label(root, text="Threshold[%]")
label_n = Label(root, text="Measurement number")
label_ex = Label(root, text=explanation, anchor="w", justify="left", width=60)
tb1 = Entry(root)
tb2 = Text(root, width=24, height=10.5)
lb = Listbox(root)
s1 = Scale(root, orient='h', from_=0, to=100, command=change_threshold, length=200)
s2 = Scale(root, orient='h', from_=20, to=50, command=change_mesurement_n, length=200)

# ----------------------------------- main ----------------------------------------- #

if __name__ == "__main__":
    # Arrangement
    button1.grid(row=0, column=0, padx=5, pady=5)
    button2.grid(row=0, column=1, padx=5, pady=5)
    button3.grid(row=1, column=0, padx=5, pady=5)
    button4.grid(row=1, column=1, padx=5, pady=5)
    button5.grid(row=2, column=0, padx=5, pady=5)
    button6.grid(row=2, column=1, padx=5, pady=5)
    cb.grid(row=3, column=0, padx=5, pady=5, columnspan=5)
    tb1.grid(row=4, column=0, padx=5, pady=5, columnspan=5)
    lb.grid(row=5, column=0)
    tb2.grid(row=5, column=1)
    label_th.grid(row=6, columnspan=8, ipadx=0)
    s1.grid(row=7, columnspan=8, ipadx=0)
    label_n.grid(row=8, columnspan=8, ipadx=0)
    s2.grid(row=9, columnspan=8, ipadx=0)
    label_ex.grid(row=10, columnspan=8, ipadx=0)
    s1.set(Min * 100)
    s2.set(50)

    # initialize
    tb1.insert(Tkinter.END, tb_defalt)
    rospy.init_node("gui")
    cb['values'] = Posenames
    th1.start()

    # main process
    root.mainloop()
    rospy.spin()
