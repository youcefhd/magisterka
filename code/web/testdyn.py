#! /usr/bin/env python2
# coding: utf-8

from webfis.models import *

from sys import argv

from numpy import *
import matplotlib.pyplot as pyplot

user = User.query.filter_by(username = argv[1]).first()
train_data = FData.query.filter_by(user_id = user.id, name= argv[3]).first().data
fis = FModel.query.filter_by(user_id = user.id, name = argv[2]).first().data

zad = []
y = []
dif = []

for data in train_data:
    zad.append(data[3])
    yi = fis.eval([data[0], data[1], data[2]])
    y.append(yi)
    dif.append(data[3] - yi)

fig = pyplot.figure(1)
pyplot.plot(zad)
pyplot.plot(y)
pyplot.plot(dif)
pyplot.xlabel("t")
pyplot.ylabel("y")

pyplot.show()