#! /usr/bin/env python2

from pyfis.struct import *

from numpy import array
import json

def fis_to_json(fis):
    j = {}
    j['defuzzmethod'] = fis.defuzzmethod
    j['funtype'] = fis.funtype
    inputs = []
    for inp in fis.inputs:
        input = []
        for mf in inp.mem_func:
            memfunc = {}
            memfunc['type'] = type(mf).__name__
            memfunc['params'] = mf.params.tolist()
            input.append(memfunc)
        inputs.append(input)
    j['inputs'] = inputs
    rules = []
    for r in fis.rules:
        rule = {}
        rule['params'] = r.params.tolist()
        inputs = []
        for inp in r.inputs:
            f, m = inp
            inputs.append([f, m])
        rule['inputs'] = inputs
        rules.append(rule)
    j['rules'] = rules
    
    return json.dumps(j)

# helper to choose membership function constructor
constructors = {TriangleMemFunc.__name__: TriangleMemFunc, \
                TrapezoidMemFunc.__name__: TrapezoidMemFunc, \
                BellMemFunc.__name__: BellMemFunc}
  
def json_to_fis(j):
    f = json.loads(j)
    fis = Fis()
    fis.defuzzmethod = f['defuzzmethod']
    fis.funtype = f['funtype']
    for inp in f['inputs']:
        input = Input()
        for mf in inp:
            input.mem_func.append(constructors[mf['type']](array(mf['params'])))
        fis.inputs.append(input)
    for r in f['rules']:
        rule = Rule(array(r['params']))
        for inp in r['inputs']:
            rule.inputs.append((inp[0], inp[1]))
        fis.rules.append(rule)
    return fis