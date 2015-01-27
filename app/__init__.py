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
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

# initialize a loginmanager object
lm = LoginManager()
# initialize the app w/ that object
lm.init_app(app)
# let flask-login know what view logs users in
lm.login_view = 'login'
# initialize openid object - requires a path to a temp folder where files can be stored
oid = OpenID(app, os.path.join(basedir, 'tmp'))

# Sending logging to e-mail
# if not app.debug:
# 	import logging
# 	from logging.handlers import SMTPHandler
# 	credentials = None
# 	if MAIL_USERNAME or MAIL_PASSWORD:
# 		credentials = (MAIL_USERNAME, MAIL_PASSWORD)
# 	mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 
# 								'no-reply@%s' % (MAIL_SERVER),
# 								ADMINS,
# 								'micro blog failure',
# 								credentials)
# 	mail_handler.setLevel(logging.ERROR)
# 	app.logger.addHandler(mail_handler)

if not app.debug:
	import logging
	from logging.handlers import RotatingFileHandler
	# limit the size to 1MB; keep last 10 logs as backups
	file_handler = RotatingFileHandler(os.path.join(basedir, 'tmp/microblog.log'), 'a', 1 * 1024 * 1024, 10)
	# custom formatting of the messages
	# timestamp, logging level, file and line number, log msg and stack trace
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	app.logger.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info('microblog startup')



# from the app module - app.py - import views (which will be created by us)
# import models for dbs - this is created by us
from app import views, models