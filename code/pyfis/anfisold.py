#! /usr/bin/env python
# anfis.py
# coding: utf-8
import numpy as np
from struct import *

def train(fis, train_data, epochs=50, n=1, num_of_backprops=3):
    for i in range(epochs):
        print("epoch"+str(i))
        least_squares(fis, train_data)
        print("**lsq done")
        for j in range(num_of_backprops):
            backpropagate(fis, train_data, n)
            print("**backprop done")
            
def least_squares(fis, train_data):
    from scipy.linalg import pinv2
    
    # matrix initialization
    if fis.funtype == "const":
        # matrix size pxr
        A = np.zeros((len(train_data), len(fis.rules)))
    else:
        # matrix size: px(n+1)r
        A = np.zeros((len(train_data), len(fis.rules)*len(train_data[0])))
    d = np.zeros(len(train_data))
    n = len(train_data[0])-1
    
    for i in range(len(train_data)):
        # membership functions
        mi = np.array([[mf.eval(train_data[i][j]) for mf in fis.inputs[j].mem_func] \
                for j in range(n)])
        
        # activation levels
        w = np.zeros(len(fis.rules))
        for k in range(len(fis.rules)):
            inps = fis.rules[k].inputs
            w[k] = mi[inps[0][0]][inps[0][1]]
            for j in range(1, len(inps)):
                w[k] *= mi[inps[j][0]][inps[j][1]]
                
        # A matrix setting
        if fis.funtype == "const":
            if fis.defuzzmethod == "prod":
                A[i] = np.array(w)
            else:
                A[i] = np.array([w[k]/sum(w) for k in range(len(fis.rules))])
        else:
            for k in range(len(fis.rules)):
                if fis.defuzzmethod == "prod":
                    A[i][k*(n+1)] = w[k]
                else:
                    A[i][k*(n+1)] = w[k]/sum(w)
                for j in range(n):
                    if fis.defuzzmethod == "prod":
                        A[i][k*(n+1)+j+1] = w[k]*train_data[i][j]
                    else:
                        A[i][k*(n+1)+j+1] = w[k]*train_data[i][j]/sum(w)
        d[i] = train_data[i][-1]
    
    Ap = pinv2(A)
    p = np.mat(Ap)*np.mat(d).transpose()
    
    pm = p.getA1()
    for i in range(len(fis.rules)):
        for j in range(len(fis.rules[i].params)):
            fis.rules[i].params[j] = pm[i*(n+1)+j]

def backpropagate(fis, train_data, n):    
    # shuffling train data
    np.random.shuffle(train_data)
    
    for data in train_data:
        # membership functions
        mi = np.array([[mf.eval(data[i]) for mf in fis.inputs[i].mem_func] \
                for i in range(len(data)-1)])
        # membership functions gradient
        dmi = np.array([[mf.grad(data[i]) for mf in fis.inputs[i].mem_func] \
                for i in range(len(data)-1)])
        # activation levels
        w = np.empty(len(fis.rules))
        for k in range(len(fis.rules)):
            inps = fis.rules[k].inputs
            w[k] = mi[inps[0][0]][inps[0][1]]
            for j in range(1, len(inps)):
                w[k] *= mi[inps[j][0]][inps[j][1]]
        # output function values
        yi = np.array([rule.evalout(data[0:-1]) for rule in fis.rules])
        # output from system
        y = fis.eval(data[0:-1])
        
        # gradient vector initialization
        dE = [[[0 for param in mf.params] for mf in inp.mem_func] for inp in fis.inputs]
        # gradient calculation
        if fis.defuzzmethod == "aver":
            for j in range(len(fis.inputs)): # inputs
                for i in range(len(fis.inputs[j].mem_func)): # mem_functions
                    for p in range(len(fis.inputs[j].mem_func[i].params)): # params
                        for r in range(len(fis.rules)): #rules
                            dws = 0 # derivative of sum of w
                            # search for rule(s) containing param
                            for rule in fis.rules:
                                if (j, i) in rule.inputs:
                                    dwk = 1
                                    for inp in rule.inputs:
                                        if inp == (j, i):
                                            dwk *= dmi[j][i][p]
                                        else:
                                            dwk *= mi[inp[0]][inp[1]]
                                    dws += dwk
                            if (j, i) in fis.rules[r].inputs:
                                dwi = 1 # derivative of current w
                                for inp in fis.rules[r].inputs:
                                    if inp == (j, i):
                                        dwi *= dmi[j][i][p]
                                    else:
                                        dwi *= mi[inp[0]][inp[1]]
                            else:
                                dwi = 0
                            
                            dwr = (sum(w)*dwi - w[r]*dws)/(sum(w)**2)
                            dE[j][i][p] += yi[r]*dwr
                        dE[j][i][p] *= (y-data[-1])
        else:
            for j in range(len(fis.inputs)): # inputs
                for i in range(len(fis.inputs[j].mem_func)): # mem_functions
                    for p in range(len(fis.inputs[j].mem_func[i].params)): # params
                        for r in range(len(fis.rules)): #rules
                            if (j, i) in fis.rules[r].inputs:
                                dwr = 1
                                for inp in fis.rules[r].inputs:
                                    if inp == (j, i):
                                        dwr *= dmi[j][i][p]
                                    else:
                                        dwr *= mi[inp[0]][inp[1]]
                            else:
                                dwr = 0
                            dE[j][i][p] += yi[r]*dwr
                        dE[j][i][p] *= (y-data[-1])
        
        # update of membership functions parameters
        for j in range(len(fis.inputs)): # inputs
            for i in range(len(fis.inputs[j].mem_func)): # mem_functions
                for p in range(len(fis.inputs[j].mem_func[i].params)): # params
                    fis.inputs[j].mem_func[i].params[p] -= n*dE[j][i][p]
                    
