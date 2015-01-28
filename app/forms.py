# Form class from wtf - used to create form objects
from flask.ext.wtf import Form
# different field classes to be used in forms
from wtforms import StringField, BooleanField, TextAreaField
# function attached to fields to perform automatic
# validation on data submitted by users
from wtforms.validators import DataRequired, Length

from app.models import User

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

	def __init__(self, original_nickname, *args, **kwargs):
		"""Overriding initialization of form. 
		   Now takes original_nickname as an argument."""
		Form.__init__(self, *args, **kwargs)
		self.original_nickname = original_nickname

	# Custom validation
	def validate(self):
		"""Validate the edit form."""
		# Invalid if not valid in the first place.
		if not Form.validate(self):
			return False
		# Valid if user keeps the original name.
		if self.nickname.data == self.original_nickname:
			return True
		# Determine if nickname's already in use.
		user = User.query.filter_by(nickname=self.nickname.data).first()
		# If it is, ask them to pick another name.
		if user != None:
			self.nickname.errors.append('This nickname is already in use. Please choose another one.')
			return False
		# If it passes everything, it's validated.
		return True

class PostForm(Form):
	"""Form for creating posts."""
	
	post = StringField('post', validators=[DataRequired()])