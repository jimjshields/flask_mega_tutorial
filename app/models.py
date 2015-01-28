# from the app module, import the db object (a sqlalchemy object)
from app import db
# md5 is a hash function that will hash an email and pass it to gravatar
from hashlib import md5

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
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)

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

	def avatar(self, size):
		"""Returns the avatar for the hashed e-mail.
		   If there's no account, return 'mm' (aka mystery man) avatar."""
		return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
			(md5(self.email.encode('utf-8')).hexdigest(), size)

	# tell python how to print the objects of this class
	def __repr__(self):
		return '<User %r>' % (self.nickname)

	# Doesn't apply to an instance of the User class, so make it a static method.
	@staticmethod
	def make_unique_nickname(nickname):
		"""Given a nickname, check if it's already been taken.
		   If it has, find the next available number for that nickname
		   and return the nickname plus that new number."""
		if User.query.filter_by(nickname=nickname).first() is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname=new_nickname).first() is None:
				break
			version += 1
		return new_nickname

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)