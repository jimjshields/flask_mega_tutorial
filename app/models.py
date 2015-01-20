# from the app module, import the db object (a sqlalchemy object)
from app import db

# each class represents a table - define a table here
class User(db.Model):
	# each attribute is a field
	# can specify sql constraints/etc.
	id = db.Column(db.Integer, primary_key=True)
	# can specify other attributes (whether it's indexed, a primary key, etc.)
	nickname = db.Column(db.String(64), index=True, unique=True)
	# or maximum length
	email = db.Column(db.String(120), index=True, unique=True)
	# foreign key - one to many relationship - defined on the 'one' side
	# first argument - 'many' class of the relationship
	# backref - field that is added to objects of 'many' class
	# in this case, can use post.author to get the user instance of the post
	posts = db.relationship('Post', backref='author', lazy='dynamic')

	### Flask-Login methods ###

	# misleading name - should return True unless a particular user
	# shouldn't be authenticated for some reason
	def is_authenticated(self):
		return True

	# True unless they are inactive - e.g., they're banned
	def is_active(self):
		return True

	# True only for fake users not allowed to log in
	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	# tell python how to print the objects of this class
	def __repr__(self):
		return '<User %r>' % (self.nickname)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)