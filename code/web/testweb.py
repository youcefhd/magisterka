#! /usr/bin/env python2
# coding: utf-8

from webfis.models import *

from sys import argv

from numpy import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib.pyplot as pyplot

user = User.query.filter_by(username = argv[1]).first()
train_data = FData.query.filter_by(user_id = user.id, name= argv[3]).first().data
fis = FModel.query.filter_by(user_id = user.id, name = argv[2]).first().data

X = arange(-9.99, 10.01, 2)
Y = arange(-9.99, 10.01, 2)
X, Y = meshgrid(X, Y)
Z = X.copy()
for i in range(len(X)):
    for j in range(len(X[i])):
        Z[i][j] = fis.eval([X[i][j], Y[i][j]])

fig = pyplot.figure(3)
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0, antialiased=False)
ax.set_xlabel("x")
ax.set_ylabel("y")

pyplot.show()