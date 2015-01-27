# Form class from wtf - used to create form objects
from flask.ext.wtf import Form
# different field classes to be used in forms
from wtforms import StringField, BooleanField, TextAreaField
# function attached to fields to perform automatic
# validation on data submitted by users
from wtforms.validators import DataRequired, Length

# login form class - inherits from Form class
class LoginForm(Form):
	# field is called openid
	# validator just ensures the field isn't empty
	openid = StringField('openid', validators=[DataRequired(message="testing")])
	# field is called remember_me, either True or False
	remember_me = BooleanField('remember_me', default=False)

class EditForm(Form):
	nickname = StringField('nickname', validators=[DataRequired()])
	about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])