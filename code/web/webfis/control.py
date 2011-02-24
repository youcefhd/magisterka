#! /usr/bin/env python2

from functools import wraps
from flask import url_for, request, redirect, session, render_template, flash

from webfis import app
from webfis.models import *

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
    return render_template('index.html')

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

