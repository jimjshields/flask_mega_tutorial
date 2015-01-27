### Run the application in production. ###

# make this executable
#!flask/bin/python

# import the app object from the app module
print "importing app from app"
from app import app

# if this script is run, start the server with debug off
# leaving debug on is extremely dangerous in production
print "running the app"
app.run(debug=False)