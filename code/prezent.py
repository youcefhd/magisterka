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

# generacja danych trenujących
train_data = []

for x in arange(-10.01, 11, 2):
    for y in arange(-10.01, 11, 2):
        train_data.append([x, y, (sin(x)*sin(y))/(x*y)])
train_data = array(train_data)

# generacja danych testowych
X = arange(-10.01, 11, 2)
Y = arange(-10.01, 11, 2)
X, Y = meshgrid(X, Y)
Z1 = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z1[i][j] = (sin(X[i][j])*sin(Y[i][j]))/(X[i][j]*Y[i][j])

fig = pyplot.figure(1)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z1, rstride=1, cstride=1, linewidth=0.5, antialiased=False, cmap = cm.get_cmap('Spectral'))
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

Z2 = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z2[i][j] = fis.eval([X[i][j], Y[i][j]])

fig = pyplot.figure(3)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z2, rstride=1, cstride=1, linewidth=0.5, antialiased=False, cmap = cm.get_cmap('Spectral'))
ax.set_xlabel("x")
ax.set_ylabel("y")

# trenowanie
train(fis, train_data, epochs=30, n=1, num_of_backprops=5)

Z3 = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z3[i][j] = fis.eval([X[i][j], Y[i][j]])

fig = pyplot.figure(4)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z3, rstride=1, cstride=1, linewidth=0.5, antialiased=False, cmap = cm.get_cmap('Spectral'))
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

# błąd
Z4 = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z4[i][j] = (Z3[i][j] - Z1[i][j])**2

fig = pyplot.figure(5)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z4, rstride=1, cstride=1, linewidth=0.5, antialiased=False, cmap = cm.get_cmap('Spectral'))
ax.set_xlabel("x")
ax.set_ylabel("y")

## wyświetlenie wykresów
pyplot.show()
