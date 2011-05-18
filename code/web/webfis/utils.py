#! /usr/bin/env python2

from pyfis.struct import *
from pyfis.anfis import *
from pyfis.evofis import *

from numpy import array, seterr, copy
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

    def __init__(self, user_id, model_id, fis, train_data, epochs=50, n=0.01, num_of_backprops=3, method="sd", num=0):
        self.user_id = user_id
        self.model_id = model_id
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
            print(i)
            if check_end(self.num):
                break
            error = calc_error(self.fis, self.train_data)
            send_error(self.num, error)
            least_squares(self.fis, self.train_data)

            if self.method == "sd":
                error = calc_error(self.fis, self.train_data)
                l = self.n
                for j in xrange(self.num_of_backprops):
                    for data in self.train_data:
                        dE = backpropagate(self.fis, data)
                        steepest_descent(self.fis, dE, l)
                    new_error = calc_error(self.fis, self.train_data)
                    if new_error < error:
                        error = new_error
                        l *= 10
                    if new_error > error:
                        error = new_error
                        l = l/10
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
        save_fis(self.fis, self.user_id, self.model_id)
        send_error(self.num, "end")

class EvoTrainer(Process):
    def __init__(self, user_id, model_id, fis, train_data, params_min, params_max, pop_size=100, crossing_size=80, mut_prob=0.1, fis_count=10, lmax=100, strategy="ml", num=0):
        self.user_id = user_id
        self.model_id = model_id
        self.fis = fis
        self.train_data = train_data
        self.params_min = params_min
        self.params_max = params_max
        self.pop_size = pop_size
        self.crossing_size = crossing_size
        self.fis_count = fis_count
        self.lmax = lmax
        self.strategy = strategy
        self.mut_prob = mut_prob
        self.num = num
        Process.__init__(self)

    def run(self):
        seterr(divide = 'raise')
        params_min = []
        params_max = []
        for input in self.fis.inputs:
            for mem_func in input.mem_func:
                params_min.extend(self.params_min)
                params_max.extend(self.params_max)        
        population = generate_population(params_min, params_max, self.pop_size - self.fis_count)
        vec = fis_to_vector(self.fis)
        for i in xrange(self.fis_count):
            population.append(copy(vec))

        for l in xrange(self.lmax):
            if check_end(self.num):
                break
            # mutation
            for p in population:
                if rand() < self.mut_prob:
                    p = mutate(p, l, self.lmax, params_min, params_max)
            # crossing over
            k = 0
            new_population = []
            while k < self.crossing_size:
                p1 = population.pop(randint(0, len(population)))
                p2 = population.pop(randint(0, len(population)))
                for p in cross(p1, p2):
                    new_population.append(p)
                if self.strategy == "m+l":
                    new_population.append(p1)
                    new_population.append(p2)
                k += 2
            if self.strategy == "m+l":
                new_population.extend(population)
            #eliminating
            prob = []
            sum = 0
            avgsum = 0
            num = 0
            min = float("infinity")
            for p in new_population:
                err = calc_error(vector_to_fis(self.fis, p, self.train_data), self.train_data)
                print(err)
                if err < min:
                    min = err
                qual = 1/err
                sum += qual
                avgsum += err
                num += 1
                prob.append(sum)
            population = []
            avg = avgsum / num
            print(self.num)
            print(avg, min)
            send_error(self.num, (avg, min))
            for i in xrange(self.pop_size):
                r = rand()*sum
                j = 0
                while(j < len(new_population)-1 and prob[j] < r):
                    j += 1
                population.append(new_population.pop(j))
                qual = prob.pop(j)
                while(j < len(new_population)):
                    prob[j] -= qual
                    j += 1
                sum -= err
        save_fis(self.fis, self.user_id, self.model_id)
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
                          routing_key="end"+str(num),
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
                        queue="end"+str(num),
                        exchange="end",
                        routing_key="end"+str(num),
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

def save_fis(fis, user_id, model_id):
    fmodel = FModel.query.filter_by(user_id=user_id, id=model_id).first()
    fmodel.data = fis
    db.session.commit()
