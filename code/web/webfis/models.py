#! /usr/bin/env python2

from flaskext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from webfis import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webfis_data.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    pw_hash = db.Column(db.String(80))
    fmodels = db.relationship("FModel", order_by="FModel.id", backref="user")
    fdatas = db.relationship("FData", order_by="FData.id", backref="user")

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

class FModel(db.Model):
    __tablename__ = "models"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    data = db.Column(db.PickleType(mutable=False))

    def __init__(self, user_id, name, fis):
        self.user_id = user_id
        self.name = name
        self.data = fis

class FData(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    data = db.Column(db.PickleType(mutable=False))

    def __init__(self, user_id, name, data):
        self.user_id = user_id
        self.name = name
        self.data = data

