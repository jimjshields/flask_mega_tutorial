# render_template allows you to create dynamic html templates by passing 
# python data to the template and calling that data in the template
from flask import render_template
# import the app variable - aka the Flask object - from the app module
from app import app

# url routing decorator - decorates the function below it 
# by assigning it a route (here, '/')
@app.route('/')
# add another possible route - '/index' - 
# that will point to the same function
@app.route('/index')
# the routing function - when you go to the above urls,
# the below function returns what will be rendered as html
def index():
	# dictionary variable that can be passed to the template
	user = {'nickname': 'Miguel'} # fake user
	# render_template will take the page specified and
	# plug the variable blocks in the template w/ the data passed
	# to the function
	return render_template('index.html', title='Home', user=user)