#! /usr/bin/env python2
# coding: utf-8
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib.pyplot as pyplot
import numpy as np
from pyfis.struct import *

fis = Fis(defuzzmethod="aver")

inp = Input()
mf = TrapezoidMemFunc([-1.0, 0.0, 2.0, 3.0])
inp.mem_func.append(mf)
mf2 = TriangleMemFunc([2.0, 3.0, 4.0])
inp.mem_func.append(mf2)
mf3 = TrapezoidMemFunc([3.0, 4.0, 6.0, 7.0])
inp.mem_func.append(mf3)
fis.inputs.append(inp)

inp2 = Input()
mf21 = TrapezoidMemFunc([-1.0, 0.0, 3.0, 4.0])
mf22 = TrapezoidMemFunc([3.0, 4.0, 6.0, 7.0])
inp2.mem_func.append(mf21)
inp2.mem_func.append(mf22)
fis.inputs.append(inp2)

rule = Rule([1.0])
rule.inputs.append((0, 0))
rule.inputs.append((1, 0))
fis.rules.append(rule)
rule1 = Rule([1.0])
rule1.inputs.append((0, 0))
rule1.inputs.append((1, 1))
fis.rules.append(rule1)
rule2 = Rule([5.0])
rule2.inputs.append((0, 1))
rule2.inputs.append((1, 0))
fis.rules.append(rule2)
rule3 = Rule([4.0])
rule3.inputs.append((0, 1))
rule3.inputs.append((1, 1))
fis.rules.append(rule3)
rule4 = Rule([2.0])
rule4.inputs.append((0, 2))
rule4.inputs.append((1, 0))
fis.rules.append(rule4)
rule5 = Rule([1.0])
rule5.inputs.append((0, 2))
rule5.inputs.append((1, 1))
fis.rules.append(rule5)

#test właściwy
X = np.arange(0, 6, 0.1)
Y = np.arange(0, 6, 0.1)
X, Y = np.meshgrid(X, Y)
Z = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z[i][j] = fis.eval([X[i][j], Y[i][j]])

fig = pyplot.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)
pyplot.show()
