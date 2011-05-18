#! /usr/bin/env python2

from functools import wraps
from flask import *
from scipy.io import loadmat

from webfis import app
from webfis.models import *
from webfis.utils import *

from pyfis.struct import *
from pyfis.anfis import calc_error

import json

app.secret_key = '&8\x7f\xd2Wo\x80\xec\xa3EG\xa6\xa9\xde\x16\xed\x0cF\xfav\x08&]\xf5'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    user = User.query.filter_by(username=session['username']).first()
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if not user:
            error = 'Invalid username or password'
        elif not user.check_password(request.form['password']):
            error = 'Invalid username or password'
        else:
            session['username'] = user.username
            flash('You were logged in')
            return redirect(request.args['next'])
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    error = None
    if request.method == 'POST':
        if request.form['password1'] != request.form['password2']:
            error = 'Invalid password'
        elif User.query.filter_by(username=request.form['username']).first():
            error = 'Requested user name is already taken'
        else:
            user = User(request.form['username'], request.form['password1'])
            db.session.add(user)
            db.session.commit()
            session['username'] = user.username
            flash('New account succesfully created')
            return redirect(url_for('index'))
    return render_template('newuser.html', error=error)

@app.route('/deluser', methods=['GET', 'POST'])
@login_required
def deluser():
    if request.method == 'POST':
        if request.form['delete'] == 'Delete':
            user = User.query.filter_by(username=session['username']).first()
            db.session.delete(user)
            db.session.commit()
            session.pop('username', None)
            flash('Account succesfully deleted')
        return redirect(url_for('index'))
    return render_template('deluser.html')

@app.route('/newdata', methods=['GET', 'POST'])
@login_required
def newdata():
    user = User.query.filter_by(username=session['username']).first()
    error = None
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            error = "File not specified!"
        elif FData.query.filter_by(user_id=user.id, name=request.form['fdataname']).first():
            error = "Data set with given name already exists!"
        elif request.form['filetype'] == 'mat':
            values = loadmat(file.stream)
            if request.form['matvar'] not in values:
                error = "No variable " + request.form['matvar'] + " in specified file!"
            else:
                fdata = FData(user.id, request.form['fdataname'], values[request.form['matvar']])
                db.session.add(fdata)
                db.session.commit()
                flash('New data set succesfully added')
                return redirect(url_for('showdata', data_id=fdata.id))
        else:
            error = "Not implemented yet!"
    return render_template('newdata.html', user=user, error=error)

@app.route('/showdata/<int:data_id>')
@login_required
def showdata(data_id):
    user = User.query.filter_by(username=session['username']).first()
    fdata = FData.query.filter_by(user_id=user.id, id=data_id).first()
    return render_template('showdata.html', user=user, data=fdata)

@app.route('/deldata/<int:data_id>', methods=['GET', 'POST'])
@login_required
def deldata(data_id):
    user = User.query.filter_by(username=session['username']).first()
    fdata = FData.query.filter_by(user_id=user.id, id=data_id).first()
    if request.method == 'POST':
        if request.form['delete'] == 'Delete':
            db.session.delete(fdata)
            db.session.commit()
            flash('Data set succesfully deleted')
        return redirect(url_for('index'))
    return render_template('deldata.html', user=user, data=fdata)

@app.route('/newmodel', methods=['GET', 'POST'])
@login_required
def newmodel():
    user = User.query.filter_by(username=session['username']).first()
    error = None
    if request.method == 'POST':
        if FModel.query.filter_by(user_id=user.id, name=request.form['fmodelname']).first():
            error = "Model with given name already exists!"
        else:
            fmodel = FModel(user.id, request.form['fmodelname'], \
                Fis(defuzzmethod = request.form['defuzzmethod'], funtype = request.form['funtype']))
            db.session.add(fmodel)
            db.session.commit()
            flash('New model succesfully added')
            return redirect(url_for('showmodel', model_id=fmodel.id))
    return render_template('newmodel.html', user=user, error=error)

@app.route('/showmodel/<int:model_id>')
@login_required
def showmodel(model_id):
    user = User.query.filter_by(username=session['username']).first()
    fmodel = FModel.query.filter_by(user_id=user.id, id=model_id).first()
    return render_template('showmodel.html', user=user, model=fmodel)

@app.route('/delmodel/<int:model_id>', methods=['GET', 'POST'])
@login_required
def delmodel(model_id):
    user = User.query.filter_by(username=session['username']).first()
    fmodel = FModel.query.filter_by(user_id=user.id, id=model_id).first()
    if request.method == 'POST':
        if request.form['delete'] == 'Delete':
            db.session.delete(fmodel)
            db.session.commit()
            flash('Model set succesfully deleted')
        return redirect(url_for('index'))
    return render_template('delmodel.html', user=user, model=fmodel)

@app.route('/getfis/<int:model_id>')
@login_required
def getfis(model_id):
    user = User.query.filter_by(username=session['username']).first()
    fmodel = FModel.query.filter_by(user_id=user.id, id=model_id).first()
    return fis_to_json(fmodel.data)
    
@app.route('/updatefis/<int:model_id>', methods=['GET', 'POST'])
@login_required
def updatefis(model_id):
    user = User.query.filter_by(username=session['username']).first()
    fmodel = FModel.query.filter_by(user_id=user.id, id=model_id).first()
    if request.method == 'POST':
        fmodel.data = json_to_fis(request.form['fis'])
        db.session.commit()
        return make_response('OK', 200)
    abort(500)
    
@app.route('/starttrain/<int:model_id>', methods=['GET', 'POST'])
@login_required
def starttrain(model_id):
    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        fmodel = FModel.query.filter_by(user_id=user.id, id=model_id).first()
        fdata = FData.query.filter_by(user_id=user.id, id=request.form['data_id']).first()
        fis = fmodel.data
        train_data = fdata.data
        epochs = int(request.form['epochs'])
        n = float(request.form['n'])
        num_of_backprops = int(request.form['num_of_backprops'])
        method = request.form['method']
        
        num = get_next_number()
        trainer = Trainer(user.id, fmodel.id, fis, train_data, epochs, n, num_of_backprops, method, num)
        trainer.start()
        
        return redirect(url_for('watchtrain', num=num))
    return render_template('starttrain.html', user=user, model_id=model_id)

    
@app.route('/watchtrain/<int:num>')
@login_required
def watchtrain(num):
    user = User.query.filter_by(username=session['username']).first()
    return render_template('watchtrain.html', user=user, num=num)
    
@app.route('/gettrainerror/<int:num>')
@login_required
def gettrainerror(num):
    error = get_error(num)
    return json.dumps(error)
    
@app.route('/endtrain/<int:num>')
@login_required
def endtrain(num):
    send_end(num)
    return make_response('OK', 200)
    
@app.route('/startevotrain/<int:model_id>', methods=['GET', 'POST'])
@login_required
def startevotrain(model_id):
    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        fmodel = FModel.query.filter_by(user_id=user.id, id=model_id).first()
        fdata = FData.query.filter_by(user_id=user.id, id=request.form['data_id']).first()
        fis = fmodel.data
        train_data = fdata.data
        params_min = json.loads(request.form['params_min'])
        params_max = json.loads(request.form['params_max'])
        pop_size = int(request.form['pop_size'])
        crossing_size = int(request.form['crossing_size'])
        fis_count = int(request.form['fis_count'])
        lmax = int(request.form['lmax'])
        strategy = request.form['strategy']
        mut_prob = float(request.form['mut_prob'])
        
        num = get_next_number()
        trainer = EvoTrainer(user.id, fmodel.id, fis, train_data, params_min, params_max, pop_size, crossing_size, mut_prob, fis_count, lmax, strategy, num)
        print("before start")
        trainer.start()
        print("after start")
        
        return redirect(url_for('watchevotrain', num=num))
    return render_template('startevotrain.html', user=user, model_id=model_id)
    
@app.route('/watchevotrain/<int:num>')
@login_required
def watchevotrain(num):
    user = User.query.filter_by(username=session['username']).first()
    return render_template('watchevotrain.html', user=user, num=num)
    
@app.route('/test/<int:model_id>/<int:data_id>')
@login_required
def test(model_id, data_id):
    user = User.query.filter_by(username=session['username']).first()
    fmodel = FModel.query.filter_by(user_id=user.id, id=model_id).first()
    fdata = FData.query.filter_by(user_id=user.id, id=data_id).first()
    return json.dumps(calc_error(fmodel.data, fdata.data))
    
