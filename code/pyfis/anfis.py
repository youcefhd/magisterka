#! /usr/bin/env python2
# anfis.py
# coding: utf-8
from numpy import *
from numpy.linalg import inv
from scipy.linalg import pinv2
from struct import *

def train(fis, train_data, epochs=50, n=1, num_of_backprops=3, method="sd"):
    for i in xrange(epochs):
        print("epoch"+str(i))
        least_squares(fis, train_data)
        print("**lsq done")
        
        if method == "sd":
            for j in xrange(num_of_backprops):
                for data in train_data:
                    dE = backpropagate(fis, data)
                    steepest_descent(fis, dE, n)
                print".",
        if method == "lm":
            error = calc_error(fis, train_data)
            l = 1
            for j in xrange(num_of_backprops):
                for data in train_data:
                    dE = backpropagate(fis, data)
                    levenberg_marquardt(fis, dE, l)
                new_error = calc_error(fis, train_data)
                if new_error < error:
                    error = new_error
                    l *= 10
                if new_error > error:
                    l = l/10
                print ".",
        print("")
            
def least_squares(fis, train_data):    
    # matrix initialization
    if fis.funtype == "const":
        # matrix size pxr
        A = empty((len(train_data), len(fis.rules)))
    else:
        # matrix size: px(n+1)r
        A = empty((len(train_data), len(fis.rules)*len(train_data[0])))
    d = empty(len(train_data))
    n = len(train_data[0])-1
    
    for i in xrange(len(train_data)):
        # membership functions
        mi = array([[mf.eval(train_data[i][j]) for mf in fis.inputs[j].mem_func] \
                for j in xrange(n)])
        
        # activation levels
        w = empty(len(fis.rules))
        for k in xrange(len(fis.rules)):
            inps = fis.rules[k].inputs
            w[k] = mi[inps[0][0]][inps[0][1]]
            for j in xrange(1, len(inps)):
                w[k] *= mi[inps[j][0]][inps[j][1]]
                
        # A matrix setting
        if fis.funtype == "const":
            if fis.defuzzmethod == "prod":
                A[i] = array(w)
            else:
                A[i] = array([w[k]/sum(w) for k in xrange(len(fis.rules))])
        else:
            for k in xrange(len(fis.rules)):
                if fis.defuzzmethod == "prod":
                    A[i][k*(n+1)] = w[k]
                else:
                    A[i][k*(n+1)] = w[k]/sum(w)
                for j in xrange(n):
                    if fis.defuzzmethod == "prod":
                        A[i][k*(n+1)+j+1] = w[k]*train_data[i][j]
                    else:
                        A[i][k*(n+1)+j+1] = w[k]*train_data[i][j]/sum(w)
        d[i] = train_data[i][-1]
    
    Ap = pinv2(A)
    p = mat(Ap)*mat(d).transpose()
    
    pm = p.getA1()
    for i in xrange(len(fis.rules)):
        for j in xrange(len(fis.rules[i].params)):
            fis.rules[i].params[j] = pm[i*(n+1)+j]

def backpropagate(fis, data):    
    
    # membership functions
    mi = array([[mf.eval(data[i]) for mf in fis.inputs[i].mem_func] \
            for i in xrange(len(data)-1)])
    # membership functions gradient
    dmi = array([[mf.grad(data[i]) for mf in fis.inputs[i].mem_func] \
            for i in xrange(len(data)-1)])
    # activation levels
    w = empty(len(fis.rules))
    for r in xrange(len(fis.rules)):
        inps = fis.rules[r].inputs
        w[r] = mi[inps[0][0]][inps[0][1]]
        for l in xrange(1, len(inps)):
            j, i = inps[l][0], inps[l][1]
            w[r] *= mi[j][i]
            
    # output function values
    yi = array([rule.evalout(data[0:-1]) for rule in fis.rules])
    # output from system
    y = fis.eval(data[0:-1])
    
    # gradient of activation levels
    dw = {}
    for r in xrange(len(fis.rules)):
        for j in xrange(len(fis.inputs)):
            for i in xrange(len(fis.inputs[j].mem_func)):
                if (j,i) in fis.rules[r].inputs:
                    for p in xrange(len(fis.inputs[j].mem_func[i].params)):
                        dw[(r,j,i,p)] = 1
                        for inp in fis.rules[r].inputs:
                            if inp == (j,i):
                                dw[(r,j,i,p)] *= dmi[j][i][p]
                            else:
                                dw[(r,j,i,p)] *= mi[inp[0]][inp[1]]
    
    # gradient calculation
    dE = {}
    wsum = sum(w)
    wsum2 = wsum**2
    for j in xrange(len(fis.inputs)): # inputs
        for i in xrange(len(fis.inputs[j].mem_func)): # mem_functions
            for p in xrange(len(fis.inputs[j].mem_func[i].params)): # params
                dE[(j,i,p)] = 0
                if fis.defuzzmethod == "aver":
                    dws = 0
                    for r in xrange(len(fis.rules)):
                        if (r,j,i,p) in dw:
                            dws += dw[(r,j,i,p)]
                    for r in xrange(len(fis.rules)): #rules
                        if (r,j,i,p) in dw:
                            dwr = (wsum*dw[(r,j,i,p)] - w[r]*dws)/wsum2
                        else:
                            dwr = (-w[r]*dws)/wsum2
                        dE[(j,i,p)] += yi[r]*dwr
                else:
                    for r in xrange(len(fis.rules)): #rules
                        if (r,j,i,p) in dw:
                            dE[(j,i,p)] += yi[r]*dw[(r,j,i,p)]
                dE[(j,i,p)] *= (y-data[-1])
    return dE

def steepest_descent(fis, dE, n):
    # update of membership functions parameters
    for j in xrange(len(fis.inputs)): # inputs
        for i in xrange(len(fis.inputs[j].mem_func)): # mem_functions
            for p in xrange(len(fis.inputs[j].mem_func[i].params)): # params
                fis.inputs[j].mem_func[i].params[p] -= n*dE[(j,i,p)]
                    

def levenberg_marquardt(fis, dE, l):
    par = []
    grad = []
    # generate params and gradient in vector form
    for j in xrange(len(fis.inputs)): # inputs
        for i in xrange(len(fis.inputs[j].mem_func)): # mem_functions
            for p in xrange(len(fis.inputs[j].mem_func[i].params)): # params
                par.append(fis.inputs[j].mem_func[i].params[p])
                grad.append(dE[(j, i, p)])
    F = matrix(par).transpose()
    D = matrix(grad).transpose()
        
    # levenberg marquardt method (simple - easier to run with small D)
    H = D*(D.transpose())
    Fnew = F - inv(H + l*eye(len(H))) * D
    
    # change fis params
    k = 0
    for j in xrange(len(fis.inputs)): # inputs
        for i in xrange(len(fis.inputs[j].mem_func)): # mem_functions
            for p in xrange(len(fis.inputs[j].mem_func[i].params)): # params
                fis.inputs[j].mem_func[i].params[p] = Fnew[k, 0]
                k += 1
    
def calc_error(fis, train_data):
    error = 0.0
    for data in train_data:
        y = fis.eval(data[0:-1])
        error += (data[-1] - y)**2
    return error
