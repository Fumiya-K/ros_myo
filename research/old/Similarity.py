import numpy as np
import scipy as sp
from math import sqrt

class Similarity():
    def __init__(self):
        self.Values = []
        self.Simiraly = []

    def Save(self, file_name):
        np.savez(file_name + "_sim.npz", x = np.array(self.Values), y = np.array(self.Simiraly))

    def Load(self, file_name):
        z = np.load(file_name + "_sim.npz")
        self.Values = z["x"].tolist()
        self.Simiraly = z["y"].tolist()

    def Add(self, v):
        sim = [0.0 for i in self.Values]
        for i in range(len(sim)):
            sim[i] = self.Coefficient(v, self.Values[i])
        self.Simiraly.append(sim)
        self.Values.append(v)

    def Set(self, value, index):
        sim = [0 for i in range(index)]
        for i in range(len(sim)):
            sim[i] = self.Coefficient(value, self.Values[i])
        self.Simiraly[index] = sim

        for i in range(len(index+1), len(self.Values)):
            s = self.Simiraly[i]
            s[index] = self.Coefficient(value, self.Values[index])
            self.Simiraly[i] = s
        
        self.Values[index] = value

    def Delete(self, index):
        self.Values.pop(index)
        self.Simiraly.pop(index)

    def Find(self, value):
        mx = -10.0
        ind = -1
        for i in range(len(self.Values)):
            coe = self.Coefficient(value, self.Values[i])
            if(coe > mx):
                mx = coe
                ind = i
        return ind, mx

    def Coefficient(self, val1, val2):
        ave1 = float(sum(val1)) / len(val1)
        ave2 = float(sum(val2)) / len(val2)
        c = 0.0
        m1 = 0.0
        m2 = 0.0

        for i in range(len(val1)):
            dif1 = val1[i] - ave1
            dif2 = val2[i] - ave2
            c += dif1 * dif2
            m1 += dif1 * dif1
            m2 += dif2 * dif2
        if m1 * m2 == 0:
            return 0
        return float(c) / float(sqrt(m1 * m2))