# render_template allows you to create dynamic html templates by passing 
# python data to the template and calling that data in the template

# flash allows you to give user feedback - not using yet

# redirect allows redirecting a particular page - not using yet
from flask import render_template, flash, redirect

# import the app variable - aka the Flask object - from the app module
from app import app

# import the LoginForm class from the forms module
from .forms import LoginForm

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
def login():
	# assign an instance of LoginForm to form
	form = LoginForm()
	
	# handling validated data
	if form.validate_on_submit():
		# store message w/ the submitted data
		# can be accessed only on the next displayed page
		flash('Login requested for OpenID="%s", remember_me="%s"' %
			 (form.openid.data, str(form.remember_me.data)))
		# redirect user to the index url
		# redirect - take user to page other than the one requested
		return redirect('/index')

	# if it doesn't validate (and on the first time), 
	# render login.html with the above form
	return render_template('login.html',
							title='Sign In',
							form=form)