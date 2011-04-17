#! /usr/bin/env python2
# evofis.py
# coding: utf-8
from numpy import *
from numpy.random import *

from struct import *

# helper to choose membership function constructor
constructors = {TriangleMemFunc.__name__: TriangleMemFunc, \
                TrapezoidMemFunc.__name__: TrapezoidMemFunc, \
                BellMemFunc.__name__: BellMemFunc}

def evo_train(fis, mparams_min, mparams_max, rparams_min, rparams_max, pop_size=100, fis_count=10, lmax=100, strategy="m+l", mut_prob=0.1):
    params_min = concatenate(mparams_min, arctan(rparams_min))
    params_max = concatenate(mparams_max, arctan(rparams_max))
    population = generate_population(params_min, params_max, pop_size - fis_count)
    vec = fis_to_vector(fis)
    for i in xrange(fis_count):
        population.append(vec.copy)
    
    for l in xrange(lmax):
        # mutation
        for p in population:
            if rand() < mut_prob:
                p = mutate(p, l, lmax, params_min, params_max)
        # crossing over
        cr = [0 for i in xrange(len(population))]
        for i in xrange(len(population)):
            if cr[i] == 1:
                continue
            

def fis_to_vector(fis):
    vec = array([])
    for inp in fis.inputs:
        for mem_func in inp.mem_func:
            vec = concatenate((vec, mem_func.params), axis=1)
    for rule in fis.rules:
        vec = concatenate((vec, arctan(rule.params)), axis=1)
    return vec

def generate_population(params_min, params_max, pop_size):
    population = []
    for i in xrange(pop_size):
        population.append(generate_random_vec(params_min, params_max))
    return population

def generate_random_vec(params_min, params_max):
    vecn = []
    for i in xrange(len(params_min)):
        vecn.append(params_min[i] + rand()*(params_max[i] - params_min[i]))
    return array(vecn)
        
def mutate(vec, l, lmax, params_min, params_max, b=1):
    w = 1 - rand()**((1-(l/lmax))**b)
    r = rand()
    vecn = []
    for i in range(len(vec)):
        if r > 0.5:
            vecn.append(vec[i] + (params_max[i] - vec[i])*w)
        else:
            vecn.append(vec[i] - (vec[i] + params_min[i])*w)
    return array(vecn)

def cross(vec1, vec2):
    r = rand()
    v1 = []
    v2 = []
    v3 = []
    v4 = []
    for i in xrange(len(vec1)):
        v1.append(r*vec1[i] + (1-r)*vec2[i])
        v2.append((1-r)*vec1[i] + r*vec2[i])
        v3.append(min(vec1[i], vec2[i]))
        v4.append(max(vec1[i], vec2[i]))
    return (array(v1), array(v2), array(v3), array(v4))