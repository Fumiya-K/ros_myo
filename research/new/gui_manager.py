#! /usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import subscribers, ttk, rospy, math, Tkinter, serial, time
import numpy as np
import threading as th
import Similarity
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import UInt8, Float32MultiArray
from ros_myo.msg import EmgArray
from copy import deepcopy
# import mbed_class

# アプリケーションクラス
# ユーザーの操作を管理する
class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        rospy.init_node("app")
        self.th1 = th.Thread(target=self.find_proc)
        self.params()
        self.sub = subscribers.EmgSubscribers()
        self.init_pose_pub = rospy.Publisher("/init_pose", UInt8, queue_size=1)
        self.finger_state_pub = rospy.Publisher("/finger_state", Float32MultiArray, queue_size=1)
        self.pack()
        self.createWidgets()
        self.tb1.insert(Tkinter.END, self.tb_defalt)
        self.cb['values'] = self.Posenames
        self.th1.start()

    # 変数を管理する
    def params(self):
        self.tb_defalt = "new pose name or filename to load and save"
        self.Min = 0.95
        self.Posenames = []
        self.finger_state = []
        self.max_power = []
        self.sim = Similarity.Similarity()
        self.st_flg = False
        self.file_name = ""
        self.portname = "/dev/ttyACM1"
        self.baudrate = 115200
        self.connected = False
        self.rpy = {"roll":0, "pitch":1, "yaw":2}

    # GUIに表示するウィジェットを生成
    def createWidgets(self):
        self.button1 = Button(self, text="Add", command=self.button1_click, height=2, width=5) # button2
        self.button2 = Button(self, text="Delete", command=self.button2_click, height=2, width=5) # button3
        self.button3 = Button(self, text="Find/Stop", command=self.button3_click, height=2, width=5)
        self.button4 = Button(self, text="Edit", command=self.button4_click, height=2, width=5)
        self.button5 = Button(self, text="init_pose", command=self.init_pose, height=2, width=5)
        self.button6 = Button(self, text="Save", command=self.save_param, height=2, width=5)
        self.button7 = Button(self, text="Load", command=self.load_param, height=2, width=5)
        self.button8 = Button(self, text="roll", command=self.change_rpy, height=2, width=5)
        self.button9 = Button(self, text="pitch", command=self.change_rpy, height=2, width=5)
        self.button10 = Button(self, text="yaw", command=self.change_rpy, height=2, width=5)
        self.button11 = Button(self, text="+", command=self.change_direction, height=2, width=5)
        self.button12 = Button(self, text="+", command=self.change_direction, height=2, width=5)
        self.button13 = Button(self, text="+", command=self.change_direction, height=2, width=5)

        def sum_str(str_arr):
            string = ""
            for i in str_arr:
                string += i
            return string

        explanations = []
        explanations.append("1. ポーズの登録\n・TextBoxに登録したいポーズの名前を入力\n・Addボタンを押し、手を登録したいポーズにする\n・テキストボックスに結果が表示されれば登録完了。ComboBoxに登録したポーズが追加される\n\n")
        explanations.append("2. ポーズの削除\n・現状、Editボタンが機能しないため、教師データを変更したい場合は削除する必要がある\n・ComboBoxから削除したいポーズを選択する\n・Deleteボタンを押し、削除する\n\n")
        explanations.append("3. ロボットハンドの状態\n・ComboBoxから設定したいポーズの名前を選択する\n・親指の回内外, 親指の屈曲, 人差し指の屈曲, 中指の屈曲, 薬指の屈曲, 小指の屈曲\n・上の順に曲げるなら1, そうでない場合は0を入力する\n・例）1, 1, 1, 0, 1, 1 \n\n")
        explanations.append("4. ポーズ判定の実行\n・Find/Stopボタンを押すとポーズ判別が開始する\n・判定を終了したい場合は同様にFind/Stopボタンを押す\n\n")
        explanations.append("5. セーブとロード\n・テキストボックスにセーブ(ロード)したいファイル名を入力し、Save(Load)ボタンを押す\n\n")
        explanation = sum_str(explanations)

        self.cb = ttk.Combobox(self)
        self.label_th = Label(self, text="Threshold[%]")
        self.label_n = Label(self, text="Measurement number")
        self.label_ex = Label(self, text=explanation, anchor="w", justify="left", width=60)
        self.tb1 = Entry(self)
        self.tb2 = Text(self, width=24, height=10.5)
        self.lb = Listbox(self)
        self.s1 = Scale(self, orient='h', from_=0, to=100, command=self.change_threshold, length=200)
        self.s2 = Scale(self, orient='h', from_=20, to=50, command=self.change_mesurement_n, length=200)
        self.s3 = Scale(self, orient="h", from_=70, to=150, command=self.change_th_power, length=200)

        self.button1.grid(row=0, column=0, padx=5, pady=5)
        self.button2.grid(row=0, column=1, padx=5, pady=5)
        self.button3.grid(row=1, column=0, padx=5, pady=5)
        self.button4.grid(row=1, column=1, padx=5, pady=5)
        self.button5.grid(row=2, column=0, padx=5, pady=5)
        self.button6.grid(row=3, column=0, padx=5, pady=5)
        self.button7.grid(row=3, column=1, padx=5, pady=5)
        self.button8.grid(row=0, column=2, padx=5, pady=5)
        self.button9.grid(row=1, column=2, padx=5, pady=5)
        self.button10.grid(row=2, column=2, padx=5, pady=5)
        self.button11.grid(row=0, column=3, padx=5, pady=5)
        self.button12.grid(row=1, column=3, padx=5, pady=5)
        self.button13.grid(row=2, column=3, padx=5, pady=5)
        self.cb.grid(row=4, column=0, padx=5, pady=5, columnspan=5)
        self.tb1.grid(row=5, column=0, padx=5, pady=5, columnspan=5)
        self.lb.grid(row=6, column=0)
        self.tb2.grid(row=6, column=1)
        self.label_th.grid(row=7, columnspan=8, ipadx=0)
        self.s1.grid(row=8, columnspan=8, ipadx=0)
        self.label_n.grid(row=9, columnspan=8, ipadx=0)
        self.s2.grid(row=10, columnspan=8, ipadx=0)
        self.s3.grid(row=11, columnspan=8, ipadx=0)
        self.label_ex.grid(row=12, columnspan=8, ipadx=0)
        self.s1.set(self.Min * 100)
        self.s2.set(50)
        self.s3.set(120)
    
    # 未実装
    def change_rpy(self):
        return

    # 未実装
    def change_direction(self):
        return

    # 手のポーズを判別するプログラム
    # 別スレッドで独立で動作している
    def find_proc(self):
        sub_win = Toplevel()
        var = StringVar()
        l = Label(sub_win, textvariable=var, font=("Helvetica", "96", "bold"))
        l.pack()
        while True:
            pre_ind = -1
            while self.st_flg:
                e = self.sub.emgs
                ind, coef = self.sim.Find(e)
                # print(ind, coef)
                if coef >= self.Min:
                    try:
                        self.tb2.delete("1.0", "end")
                        mp = float(self.max_power[ind]) * self.sub.pr
                        power_ratio = (float(sum(e)) / float(len(e))) / mp if (sum(e) / len(e)) / mp < 1.0 else 1.0
                        self.tb2.insert(END, "{} \ncoef = {}\npower ratio = {}".format(self.Posenames[ind], round(coef, 4), round(power_ratio, 4)))
                        var.set(self.Posenames[ind])
                        finger_arr = Float32MultiArray()
                        multi_power_ratio = np.array(self.finger_state[ind]) * power_ratio
                        finger_arr.data = multi_power_ratio.tolist()
                        self.finger_state_pub(finger_arr)
                    except IndexError:
                        pass

    # ポーズの登録
    def button1_click(self):
        if self.sub.EMG == None:
            return
        if self.tb1.get() == self.tb_defalt:
            self.tb2_print("Please input pose name")
        else:
            for i in range(3):
                time.sleep(1)
            self.sim.Add(deepcopy(self.sub.EMG))
            self.finger_state.append([0, 0, 0, 0, 0])
            self.max_power.append(sum(self.sub.EMG) / len(self.sub.EMG))
            self.Posenames.append(self.tb1.get())
            self.lb.insert(END, self.tb1.get())

            self.cb['values'] = self.Posenames
            self.tb1_clear()
    
    # コンボボックスで選択されているポーズを削除する
    def button2_click(self):
        num = self.cb.current()
        if num >= 0:
            self.Posenames.pop(num)
            self.finger_state.pop(num)
            self.max_power.pop(num)
            self.sim.Delete(num)
            self.cb['values'] = self.Posenames
            self.lb_update()
        
    # find_procを動作させるかの切り替え
    def button3_click(self):
        self.st_flg = not self.st_flg

    # ロボットハンドに反映するポーズを設定
    def button4_click(self):
        if self.tb1.get() == self.tb_defalt or self.cb.current == -1:
            tb2_print("Please input finger state")
            tb2_print("ex) 1 1 0 1 1 ")
        else:
            arr = self.tb1.get().split()
            print(arr)
            self.finger_state[self.cb.current()] = arr
    
    # RPYの初期位置を調整
    def init_pose(self):
        self.init_pose_pub.publish(UInt8(1))

    # 教師データを保存
    def save_param(self):
        if self.tb1.get() == self.tb_defalt:
            print("Please input file name.")
        else:
            self.file_name = self.tb1.get()
            np.savez(self.file_name + ".npz", x=np.array(self.Posenames), y=np.array(self.finger_state))
            self.sim.Save(self.file_name)
            self.tb1_clear()
            self.tb2_print("Complete")

    # 教師データの読み込み
    def load_param(self):
        if self.tb1.get() == self.tb_defalt:
            print("Please input file name.")
        else:
            self.file_name = self.tb1.get()
            self.sim.Load(self.file_name)
            zp = np.load(self.file_name+".npz")
            self.Posenames = zp["x"].tolist()
            self.finger_state = zp["y"].tolist()
            self.max_power = [sum(i) / len(i)for i in self.sim.Values]
            # print(finger_state)
            self.cb['values'] = self.Posenames
            self.lb_update()
            self.tb1_clear()
            self.tb2_print("Loaded")

    # 教師データのサンプリング数を変更
    def change_mesurement_n(self, *args):
        self.sim.measurement_n = self.s2.get()
        self.tb2_print("Mesurement Numeber = {}".format(self.sim.measurement_n))

    # 
    def change_th_power(self, *arg):
        self.sim.pr = float(self.s2.get()) / 100

    # しきい値の変更
    def change_threshold(self, *arg):
        self.Min = float(self.s1.get()) / 100
        self.tb2_print("Min = {}".format(self.Min))
    
    # TextBox1の表示をクリア
    def tb1_clear(self):
        self.tb1.delete(0, Tkinter.END)
        self.tb1.insert(Tkinter.END, self.tb_defalt)

    # TextBox2の内容を変更
    def tb2_print(self, s):
        self.tb2.insert(END, "\n{}".format(s))
        self.tb2.see("end")

    # ポーズネーズの更新
    def lb_update(self):
        self.lb.delete(0, END)
        for i in self.Posenames:
            self.lb.insert(END, i)