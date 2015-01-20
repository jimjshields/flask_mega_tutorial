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
	# "Hello, world!" is rendered as HTML
	return "Hello, world!"