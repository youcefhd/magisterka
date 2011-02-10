#! /usr/bin/env python2
# coding: utf-8

from pyfis.struct import *
from pyfis.anfis import *
from numpy import *

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib.pyplot as pyplot

# FIS with generalized bell membership functions
fis = Fis(defuzzmethod="sum")

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

# FIS with trapezoid memebrship functions
fis2 = Fis(defuzzmethod="aver")

for j in range(2):
    inp = Input()
    inp.mem_func.append(TrapezoidMemFunc([-12, -11, -10, -6]))
    inp.mem_func.append(TrapezoidMemFunc([-10, -6, -2, 2]))
    inp.mem_func.append(TrapezoidMemFunc([-2, 2, 6, 10]))
    inp.mem_func.append(TrapezoidMemFunc([6, 10, 11, 12]))
    fis2.inputs.append(inp)

for i in range(4):
    for j in range(4):
        rule = Rule([0, 0, 0])
        rule.inputs.append((0, i))
        rule.inputs.append((1, j))
        fis2.rules.append(rule)

# generacja danych trenujących
train_data = []

for x in arange(-10.01, 11, 2):
    for y in arange(-10.01, 11, 2):
        train_data.append([x, y, (sin(x)*sin(y))/(x*y)])
train_data = array(train_data)

# generacja danych testowych
X = arange(-9.99, 10.01, 2)
Y = arange(-9.99, 10.01, 2)
X, Y = meshgrid(X, Y)
Z = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z[i][j] = (sin(X[i][j])*sin(Y[i][j]))/(X[i][j]*Y[i][j])

fig = pyplot.figure(1)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)
ax.set_xlabel("x")
ax.set_ylabel("y")

# funkcje przynależności
x = arange(-10, 10, 0.1)
y = arange(-10, 10, 0.1)
# wykresy funkcji przynależności
pyplot.figure(2)
pyplot.subplot(221)
for mf in fis.inputs[0].mem_func:
    for i in range(len(x)):
        y[i] = mf.eval(x[i])
    pyplot.plot(x, y)
pyplot.xlabel("$x$")
pyplot.ylabel("$\mu_X$")
pyplot.subplot(222)
for mf in fis.inputs[1].mem_func:
    for i in range(len(x)):
        y[i] = mf.eval(x[i])
    pyplot.plot(x, y)
pyplot.xlabel("$y$")
pyplot.ylabel("$\mu_Y$")
# metoda najmniejszych kwadratów
least_squares(fis, train_data)

Z = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z[i][j] = fis.eval([X[i][j], Y[i][j]])

fig = pyplot.figure(3)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)
ax.set_xlabel("x")
ax.set_ylabel("y")
# trenowanie
train(fis, train_data, epochs=30, n=1, num_of_backprops=5)

Z = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z[i][j] = fis.eval([X[i][j], Y[i][j]])

fig = pyplot.figure(4)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)
ax.set_xlabel("x")
ax.set_ylabel("y")

# funkcje przynależności
x = arange(-10, 10, 0.1)
y = arange(-10, 10, 0.1)
# wykresy funkcji przynależności
pyplot.figure(2)

pyplot.subplot(223)
for mf in fis.inputs[0].mem_func:
    for i in range(len(x)):
        y[i] = mf.eval(x[i])
    pyplot.plot(x, y)
pyplot.xlabel("$x$")
pyplot.ylabel("$\mu_X$")
pyplot.subplot(224)
for mf in fis.inputs[1].mem_func:
    for i in range(len(x)):
        y[i] = mf.eval(x[i])
    pyplot.plot(x, y)
pyplot.xlabel("$y$")
pyplot.ylabel("$\mu_Y$")
    

## funkcje przynależności - funkcje trapezowe
#x = arange(-10, 10, 0.1)
#y = arange(-10, 10, 0.1)
## wykresy funkcji przynależności
#pyplot.figure(5)
#for j in range(len(fis2.inputs)):
    #pyplot.subplot(220+j+1)
    #for mf in fis2.inputs[j].mem_func:
        #for i in range(len(x)):
            #y[i] = mf.eval(x[i])
        #pyplot.plot(x, y)

## metoda najmniejszych kwadratów z funkcjami trapezowymi
#least_squares(fis2, train_data)
#Z = X.copy()
#for i in range(len(X)):
    #for j in range(len(X[i])):
        #Z[i][j] = fis2.eval([X[i][j], Y[i][j]])

#fig = pyplot.figure(6)
#ax = fig.gca(projection='3d')
#surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)

## trenowanie z funkcjami trapezowymi
#train(fis2, train_data, epochs=30, n=1, num_of_backprops=5)
#Z = X.copy()
#for i in range(len(X)):
    #for j in range(len(X[i])):
        #Z[i][j] = fis2.eval([X[i][j], Y[i][j]])

#fig = pyplot.figure(7)
#ax = fig.gca(projection='3d')
#surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)

## funkcje przynależności - funkcje trapezowe
#x = arange(-10, 10, 0.1)
#y = arange(-10, 10, 0.1)
## wykresy funkcji przynależności
#pyplot.figure(5)
#for j in range(len(fis2.inputs)):
    #pyplot.subplot(220+j+3)
    #for mf in fis2.inputs[j].mem_func:
        #for i in range(len(x)):
            #y[i] = mf.eval(x[i])
        #pyplot.plot(x, y)

## wyświetlenie wykresów
pyplot.show()
