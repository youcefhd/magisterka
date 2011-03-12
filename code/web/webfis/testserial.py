#! /usr/bin/env python2
# coding: utf-8

from pyfis.struct import *
from pyfis.anfis import *
from numpy import *

from utils import *

# FIS with generalized bell membership functions
fis = Fis(defuzzmethod="aver")

for j in range(2):
    inp = Input()
    for i in range(4):
        inp.mem_func.append(BellMemFunc([3.3, 4, -10+i*6.6]))
    fis.inputs.append(inp)

for i in range(4):
    for j in range(4):
        rule = Rule([0, 0, 0])
        rule.inputs.append((0, i))
        rule.inputs.append((1, j))
        fis.rules.append(rule)
        
j1 = fis_to_json(fis)
print(j1)
f = json_to_fis(j1)
j2 = fis_to_json(f)
print(j2)
print(j1 == j2)