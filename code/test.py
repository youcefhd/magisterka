#! /usr/bin/env python2
# coding: utf-8

from pyfis.struct import *
import matplotlib.pyplot as pyplot

fis = Fis(defuzzmethod="aver")

inp = Input()
mf = TrapezoidMemFunc([-1.0, 0.0, 2.0, 3.0])
inp.mem_func.append(mf)
mf2 = TrapezoidMemFunc([2.5, 3.0, 5.0, 6.0])
inp.mem_func.append(mf2)
fis.inputs.append(inp)

rule = Rule([1.0])
rule.inputs.append((0, 0))
fis.rules.append(rule)
rule2 = Rule([2.0])
rule2.inputs.append((0, 1))
fis.rules.append(rule2)

#test właściwy
x = [0.1*i for i in range(50)]
y = [0 for xi in x]
for i in range(len(x)):
    y[i] = fis.eval([x[i]])

pyplot.plot(x, y)

