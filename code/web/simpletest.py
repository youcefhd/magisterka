#! /usr/bin/env python2
# coding: utf-8

from webfis.models import *

from sys import argv
import matplotlib.pyplot as pyplot

user = User.query.filter_by(username = argv[1]).first()
train_data = FData.query.filter_by(user_id = user.id, name= argv[3]).first().data
fis = FModel.query.filter_by(user_id = user.id, name = argv[2]).first().data

x = []
y = []

for i in range(629):
    x.append(i*0.01)
    y.append(fis.eval([i*0.01]))

pyplot.figure(1)
pyplot.plot(x, y)
pyplot.show()