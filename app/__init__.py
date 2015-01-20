# Flask class allows creation of Flask objects
from flask import Flask
# sqlalchemy - for working w/ db
from flask.ext.sqlalchemy import SQLAlchemy

# Flask object of name __name__ (the name of this file)
app = Flask(__name__)
# import configuration from config module
app.config.from_object('config')
# initalize database w/ sqlalchemy
db = SQLAlchemy(app)

# from the app module - app.py - import views (which will be created by us)
# import models for dbs - this is created by us
from app import views, models

import os
# handle the users' logged in state
from flask.ext.login import LoginManager
# provide authentication
from flask.ext.openid import OpenId
# base directory of the project
from config import basedir

# initialize a loginmanager object
lm = LoginManager()
# initialize the app w/ that object
lm.init_app(app)
# initialize openid object - requires a path to a temp folder where files can be stored
oid = OpenId(app, os.path.join(basedir, 'tmp'))