#! /usr/bin/env python2

from pyfis.struct import *
from pyfis.anfis import *

from numpy import array, seterr
import json

from multiprocessing import Process
from kombu.connection import BrokerConnection
from kombu.compat import Publisher, Consumer

from models import *

def fis_to_json(fis):
    j = {}
    j['defuzzmethod'] = fis.defuzzmethod
    j['funtype'] = fis.funtype
    inputs = []
    for inp in fis.inputs:
        input = []
        for mf in inp.mem_func:
            memfunc = {}
            memfunc['type'] = type(mf).__name__
            memfunc['params'] = mf.params.tolist()
            input.append(memfunc)
        inputs.append(input)
    j['inputs'] = inputs
    rules = []
    for r in fis.rules:
        rule = {}
        rule['params'] = r.params.tolist()
        inputs = []
        for inp in r.inputs:
            f, m = inp
            inputs.append([f, m])
        rule['inputs'] = inputs
        rules.append(rule)
    j['rules'] = rules
    
    return json.dumps(j)

# helper to choose membership function constructor
constructors = {TriangleMemFunc.__name__: TriangleMemFunc, \
                TrapezoidMemFunc.__name__: TrapezoidMemFunc, \
                BellMemFunc.__name__: BellMemFunc}
  
def json_to_fis(j):
    f = json.loads(j)
    fis = Fis()
    fis.defuzzmethod = f['defuzzmethod']
    fis.funtype = f['funtype']
    for inp in f['inputs']:
        input = Input()
        for mf in inp:
            input.mem_func.append(constructors[mf['type']](array(mf['params'])))
        fis.inputs.append(input)
    for r in f['rules']:
        rule = Rule(array(r['params']))
        for inp in r['inputs']:
            rule.inputs.append((inp[0], inp[1]))
        fis.rules.append(rule)
    return fis

class Trainer(Process):
    def __init__(self, fis, train_data, epochs=50, n=1, num_of_backprops=3, method="sd", num=0):
        self.fis = fis
        self.train_data = train_data
        self.epochs = epochs
        self.n = n
        self. num_of_backprops = num_of_backprops
        self.method = method
        self.num = num
        Process.__init__(self)
    
    def run(self):
        seterr(divide = 'raise')
        for i in xrange(self.epochs):
            if check_end(self.num):
                break # TODO implement ending
            error = calc_error(self.fis, self.train_data)
            send_error(self.num, error)
            least_squares(self.fis, self.train_data)
            
            if self.method == "sd":
                for j in xrange(self.num_of_backprops):
                    for data in self.train_data:
                        dE = backpropagate(self.fis, data)
                        steepest_descent(self.fis, dE, self.n)
            if self.method == "lm":
                error = calc_error(self.fis, self.train_data)
                l = 1
                for j in xrange(self.num_of_backprops):
                    for data in self.train_data:
                        dE = backpropagate(self.fis, data)
                        levenberg_marquardt(self.fis, dE, l)
                    new_error = calc_error(self.fis, self.train_data)
                    if new_error < error:
                        error = new_error
                        l *= 10
                    if new_error > error:
                        l = l/10
                        
        send_error(self.num, "end")
    
def send_error(num, error):
    connection = BrokerConnection(hostname = 'myhost',
                                  userid = 'webfis',
                                  password = 'password',
                                  virtual_host = 'webfishost',
                                  port = 5672)
    publisher = Publisher(connection=connection,
                          exchange="error",
                          routing_key=str(num),
                          exchange_type="direct")

    publisher.send(error)
    publisher.close()
    connection.release()
    
def get_error(num):
    connection = BrokerConnection(hostname = 'myhost',
                                  userid = 'webfis',
                                  password = 'password',
                                  virtual_host = 'webfishost',
                                  port = 5672)
    consumer = Consumer(connection=connection,
                        queue=str(num),
                        exchange="error",
                        routing_key=str(num),
                        exchange_type="direct")
    
    message = consumer.fetch()
    if message:
        error = message.payload
        message.ack()
        print("geterror: " + str(error))
    else:
        error = "wait"
        
    consumer.close()
    connection.release()
    return error

def send_end(num):
    connection = BrokerConnection(hostname = 'myhost',
                                  userid = 'webfis',
                                  password = 'password',
                                  virtual_host = 'webfishost',
                                  port = 5672)
    publisher = Publisher(connection=connection,
                          exchange="end",
                          routing_key=str(num),
                          exchange_type="direct")
    
    publisher.send("end")
    publisher.close()
    connection.release()
    
def check_end(num):
    connection = BrokerConnection(hostname = 'myhost',
                                  userid = 'webfis',
                                  password = 'password',
                                  virtual_host = 'webfishost',
                                  port = 5672)
    consumer = Consumer(connection=connection,
                        queue=str(num),
                        exchange="end",
                        routing_key=str(num),
                        exchange_type="direct")
    
    message = consumer.fetch()
    if message and message.payload == "end":
        end = True
    else:
        end = False
        
    consumer.close()
    connection.release()
    return end

def get_next_number():
    seq = TrainSequence.query.first()
    num = seq.num
    seq.num = num+1
    db.session.commit()
    return num