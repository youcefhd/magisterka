#! /usr/bin/env python2
# struct.py
# coding: utf-8
from numpy import *
from time import time

""" Module containing basic classes representing Takagi-Sugeno fuzzy
interference system. """

class Fis(object):
    """Class representing fuzzy interference system"""
    
    def __init__(self, defuzzmethod="aver", funtype="lin"):
        if defuzzmethod not in ("aver", "sum"):
            raise FISException("Unknown defuzzmethod: "+defuzzmethod)
        self.defuzzmethod = defuzzmethod
        if funtype not in ("lin", "const"):
            raise FISException("Unknown lintype: "+defuzzmethod)
        self.funtype = funtype
        self.inputs = []
        self.rules = []

    def eval(self, x):
        """evaluates fuzzy system outputs"""
        # membership functions
        mi = [[mf.eval(x[i]) for mf in self.inputs[i].mem_func] \
                for i in xrange(len(x))]
        # activation levels
        w = empty(len(self.rules))
        for k in xrange(len(self.rules)):
            inps = self.rules[k].inputs
            w[k] = mi[inps[0][0]][inps[0][1]]
            for j in xrange(1, len(inps)):
                w[k] *= mi[inps[j][0]][inps[j][1]]
        # output function values
        yi = [rule.evalout(x) for rule in self.rules]
        
        # output value
        y = 0
        for k in xrange(len(yi)):
                y += w[k]*yi[k]
        if self.defuzzmethod == "aver":
            s = sum(w)
            if s!=0:
                y /= s
        
        return y

class MemFunc(object):
    """Abstract class representing membership function"""

    def __init__(self, params):
        self.params = array(params, dtype='f8')

    def eval(self, x):
        """returns membership function value"""
        pass
    
    def grad(self):
        """returns membership function gradient"""
        pass

class Input(object):
    """Class representing fuzzy system input"""
    def __init__(self):
        self.mem_func = []

class Rule(object):
    """Class representing fuzzy system rule"""

    def __init__(self, params):
        self.params = array(params, dtype='f8') # params of output, 1 if output is constant, 2*in+1 if output is
            # linearly dependent on inputs
        self.inputs = [] # tuples containing no of input and no of mem_func


    def evalout(self, x):
        y = self.params[0]
        for j in xrange(1, len(self.params)):
            y += self.params[j]*x[j-1]
        return y
    
class FISException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class TriangleMemFunc(MemFunc):
    """Triangle membership function"""

    def __init__(self, params):
        if len(params) != 3:
            raise FISException("Triangle membership function should have \
                    3 parameters!")
        self.params = array(params, dtype='f8')

    def eval(self, x):
        return max(0, min((x-self.params[0])/(self.params[1]-self.params[0]), \
                (x-self.params[2])/(self.params[1]-self.params[2])))

    def grad(self, x):
        if x<=self.params[0] or x>=self.params[2]:
            return [0, 0, 0]
        if x<=self.params[1]:
            a = (x-self.params[0])/((self.params[1]-self.params[0])**2) \
                - 1/(self.params[1]-self.params[0])
            b = -(x-self.params[0])/((self.params[1]-self.params[0])**2)
            return [a, b, 0]
        else:
            b = -(x-self.params[2])/((self.params[1]-self.params[2])**2)
            c = (x-self.params[2])/((self.params[1]-self.params[2])**2) \
                - 1/(self.params[1]-self.params[2])
            return [0, b, c]
        

class TrapezoidMemFunc(MemFunc):
    """Trapezoid membership function"""

    def __init__(self, params):
        if len(params) != 4:
            raise FISException("Trapezoid membership function should have \
                    4 parameters!")
        self.params = array(params, dtype='f8')

    def eval(self, x):
        return max(0, min((x-self.params[0])/(self.params[1]-self.params[0]), \
            1, (x-self.params[3])/(self.params[2]-self.params[3])))

    def grad(self, x):
        if x<=self.params[0] or (x<=self.params[2] and x>=self.params[1]) \
            or x>=self.params[3]:
            return [0, 0, 0, 0]
        if x<=self.params[1]:
            a = (x-self.params[0])/((self.params[1]-self.params[0])**2) \
                - 1/(self.params[1]-self.params[0])
            b = -(x-self.params[0])/((self.params[1]-self.params[0])**2)
            return [a, b, 0, 0]
        else:
            c = -(x-self.params[3])/((self.params[2]-self.params[3])**2)
            d = (x-self.params[3])/((self.params[2]-self.params[3])**2) \
                - 1/(self.params[2]-self.params[3])
            return [0, 0, c, d]

class BellMemFunc(MemFunc):
    """Generalized Bell function"""
    def __init__(self, params):
        if len(params) != 3:
            raise FISException("Bell membership function should have \
                    3 parameters!")
        self.params = array(params, dtype='f8')

    def eval(self, x):
        return 1/(1 + abs((x-self.params[2])/self.params[0])**(2*self.params[1]))

    def grad(self, x):
        a = self.params[0]
        b = self.params[1]
        c = self.params[2]
        pp = ((x-c)/a)**2
        da = (2*b*((x-c)**2)*(pp**(b-1)))/((a**3)*((pp**b+1)**2))
        db = ((pp**b)*log(pp))/((pp**b+1)**2)
        dc = (2*b*(x-c)*(pp**(b-1)))/((a**2)*((pp**b+1)**2))
        return [da, db, dc]
    