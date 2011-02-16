#! /usr/bin/env python2

from webfis import app

@app.route('/')
def hello_world():
    return "Hello World!"

