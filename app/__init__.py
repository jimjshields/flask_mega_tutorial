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

import os
# handle the users' logged in state
from flask.ext.login import LoginManager
# provide authentication
from flask.ext.openid import OpenID
# base directory of the project
from config import basedir

# initialize a loginmanager object
lm = LoginManager()
# initialize the app w/ that object
lm.init_app(app)
# let flask-login know what view logs users in
lm.login_view = 'login'
# initialize openid object - requires a path to a temp folder where files can be stored
oid = OpenID(app, os.path.join(basedir, 'tmp'))

# from the app module - app.py - import views (which will be created by us)
# import models for dbs - this is created by us
from app import views, models