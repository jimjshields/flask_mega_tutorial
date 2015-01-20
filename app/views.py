from flask import (
	render_template, # allows you to create dynamic html templates by passing python data to the template and calling that data in the template
	flash, # allows you to give user feedback
	redirect, # sends user to a page diff than the one requested
	session, # object for current session
	url_for, # gets the url for a particular view function
	request, # http request object
	g # used to store whatever you want - globally - for the life of the request
)

# flask-login-specific methods
from flask.ext.login import login_user, logout_user, current_user, login_required

# import the app variable - aka the Flask object - from the app module
from app import app, db, lm, oid

# import the LoginForm class from the forms module
from forms import LoginForm

# User class
from models import User

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
	posts = [ # fake array of posts
		{
			'author': {'nickname': 'John'},
			'body': 'Beautiful day in Portland!'
		},
		{
			'author': {'nickname': 'Susan'},
			'body': 'The Avengers movie was so cool!'
		}
	]

	# render_template will take the page specified and
	# plug the variable blocks in the template w/ the data passed
	# to the function
	return render_template('index.html',
							title='Home', 
							user=user,
							posts=posts)

# methods need to be specified if using more than GET
# POST allows user to send data through a form
@app.route('/login', methods=['GET', 'POST'])
# tells flask-openid that this is our login view function
@oid.loginhandler
def login():
	# we'll be storing the logged in user in g
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))

	# assign an instance of LoginForm to form
	form = LoginForm()
	
	# handling validated data
	if form.validate_on_submit():
		# store the session's remember_me
		session['remember_me'] = form.remember_me.data
		# tries to login with the given identity url
		# must be called from the login handler (here, oid)
		# if authentication is successful, it'll call the function
		# decorated/registered w/ oid.after_login
		return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])

	# if it doesn't validate (and on the first time), 
	# render login.html with the above form
	return render_template('login.html',
							title='Sign In',
							form=form,
							providers=app.config['OPENID_PROVIDERS'])

# registered w/ flask-login through this decorator
@lm.user_loader
# loads a user from the database
def load_user(id):
	return User.query.get(int(id))