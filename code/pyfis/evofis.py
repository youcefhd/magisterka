#! /usr/bin/env python2
# evofis.py
# coding: utf-8
from numpy import *
from numpy.random import *

from struct import *
from anfis import calc_error, least_squares

# helper to choose membership function constructor
constructors = {TriangleMemFunc.__name__: TriangleMemFunc, \
                TrapezoidMemFunc.__name__: TrapezoidMemFunc, \
                BellMemFunc.__name__: BellMemFunc}

def evo_train(fis, train_data, params_min, params_max, pop_size=100, crossing_size=80, fis_count=10, lmax=100, strategy="ml", mut_prob=0.1):
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
        k = 0
        new_population = []
        while k < crossing_size:
            p1 = population.pop(randint(0, xrange(population)))
            p2 = population.pop(randint(0, xrange(population)))
            for p in cross(p1, p2):
                new_population.append(p)
            if strategy == "m+l":
                new_population.append(p1)
                new_population.append(p2)
            k += 2
        if strategy == "m+l":
            new_population.extend(population)
        #eliminating
        prob = []
        sum = 0
        for p in new_population:
            err = calc_error(vec_to_fis(fis, p, train_data), train_data)
            sum += err
            prob.append(sum)
        population = []
        for i in len(pop_size):
            r = rand()*sum
            j = 0
            while(prob[j] < r):
                j += 1
            population.append(new_population.pop(j))
            err = error.pop(j)
            while(j < len(new_population)):
                error[j] -= err
                j += 1
            sum -= err

def fis_to_vector(fis):
    vec = array([])
    for inp in fis.inputs:
        for mem_func in inp.mem_func:
            vec = concatenate((vec, mem_func.params), axis=1)
    return vec

def vector_to_fis(fis, vec, train_data):
    vfis = Fis(defuzzmethod = fis.defuzzmethod, funtype = fis.funtype)
    parnum = 0
    for inp in fis.inputs:
        input = Input()
        for mem_func in inp.mem_func:
            params = []
            for i in xrange(len(mem_func.params)):
                params.append(vec[parnum])
                parnum += 1
            mf = constructors[type(mem_func).__name__](params)
            input.mem_func.append(mf)
        vfis.inputs.append(input)
    for r in fis.rules:
        params = [0]*len(r.params)
        rule = Rule(params)
        rule.inputs = copy(r.inputs)
        vfis.rules.append(rule)
    least_squares(vfis, train_data)
    return vfis

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
    for i in xrange(len(vec)):
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
        v1.append(vec1[i]*r + vec2[i]*(1-r))
        v2.append(vec1[i]*(1-r) + vec2[i]*r)
        v3.append(min(vec1[i], vec2[i]))
        v4.append(max(vec1[i], vec2[i]))
    return (array(v1), array(v2), array(v3), array(v4))