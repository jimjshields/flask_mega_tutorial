# Flask class allows creation of Flask objects
from flask import Flask

# Flask object of name __name__ (the name of this file)
app = Flask(__name__)

# from the app module - app.py - import views (which will be created by us)
from app import views