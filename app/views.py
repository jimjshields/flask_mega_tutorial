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
from forms import LoginForm, EditForm

# User class
from models import User

# for last_seen
from datetime import datetime

### Routing functions ###

# url routing decorator - decorates the function below it 
# by assigning it a route (here, '/')
@app.route('/')
# add another possible route - '/index' - 
# that will point to the same function
@app.route('/index')
# flask-login decorator - tells it where a login is required
@login_required
# the routing function - when you go to the above urls,
# the below function returns what will be rendered as html
def index():
	# the global user - set w/ the before_request method
	user = g.user
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
	# html_data = {
	# 		template
	# }

	return render_template('login.html',
							title='Sign In',
							form=form,
							providers=app.config['OPENID_PROVIDERS'])

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

# routing decorator with argument 'nickname'
@app.route('/user/<nickname>')
@login_required
def user(nickname):
	# sqlalchemy query
	user = User.query.filter_by(nickname=nickname).first()
	# if user not found, redirect to homepage
	if user == None:
		flash('User %s not found.' % nickname)
		return redirect(url_for('index'))
	# otherwise get user's posts and render the user template
	posts = [
		{'author': user, 'body': 'Test post #1'},
		{'author': user, 'body': 'Test post #2'}
	]
	return render_template('user.html', 
							user=user,
							posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	"""View for editing a user profile."""
	
	# Initialize form with the chosen nickname as an argument.
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit'))
	else:
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form=form)

### Following views ###

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	"""View for following the given user."""

	# Get the to-be-followed user (tbfu) from the database.
	user = User.query.filter_by(nickname=nickname).first()

	# If tbfu isn't there, redirect user.
	if user is None:
		flash('User %s not found.' % (nickname))
		return redirect(url_for('index'))

	# If user is trying to follow themself, redirect user.
	if user == g.user:
		flash('You can\'t follow yourself!')
		return redirect(url_for('user', nickname=nickname))

	# Otherwise, try to follow the tbfu.
	u = g.user.follow(user)

	# If tbfu can't be followed, redirect user.
	if u is None:
		flash('Cannot follow %s.' % (nickname))
		return redirect(url_for('user', nickname=nickname))

	# Otherwise, add follow to the database.
	db.session.add(u)
	db.session.commit()

	# Let user know.
	flash('You are now following %s!' % (nickname))
	return redirect(url_for('user', nickname=nickname))

### Custom error handlers ###

@app.errorhandler(404)
def not_found_error(error):
	"""Custom 404 error handler."""
	
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	"""Custom 500 error handler."""
	
	# If the db session encounters an error, rendering the 
	# template may require rolling it back to a working state.
	db.session.rollback()
	return render_template('500.html'), 500

### Utility functions ###

@oid.after_login
def after_login(resp):
	# if there's no email, return to login screen w/ an error
	if resp.email is None or resp.email == '':
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	# if there is one, find the email in the db
	user = User.query.filter_by(email=resp.email).first()
	if user is None:
		nickname = resp.nickname
		# if they don't give a nickname, force it from the email
		if nickname is None or nickname == '':
			nickname = resp.email.split('@')[0]
		# Make sure it's unique.
		nickname = User.make_unique_nickname(nickname)
		user = User(nickname=nickname, email=resp.email)
		
		# if the user isn't in the db,
		# add the current user to the db session
		db.session.add(user)
		db.session.commit()
		
		# Make the user follow themself.
		db.session.add(user.follow(user))
		db.session.commit()

	# default remember_me to False
	remember_me = False
	# if it's in the session, set it equal to what it is in the session
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	# redirect to the 'next' page if provided in request
	# or index if not
	return redirect(request.args.get('next') or url_for('index'))

# this decorator will run before the view function each time a request is received
@app.before_request
# set the global user var equal to current_user
# current_user is a variable set by flask-login
# so, all requests will have access to the logged in user
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		# set the last seen entry in the db to right now
		g.user.last_seen = datetime.utcnow()
		# add this entry and commit it to the db
		db.session.add(g.user)
		db.session.commit()

# registered w/ flask-login through this decorator
@lm.user_loader
# loads a user from the database
def load_user(id):
	return User.query.get(int(id))