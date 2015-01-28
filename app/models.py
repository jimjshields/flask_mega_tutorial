# from the app module, import the db object (a sqlalchemy object)
from app import db
# md5 is a hash function that will hash an email and pass it to gravatar
from hashlib import md5

# Create a followers table.
# Not a class as it's an association table - the table is only foreign keys.
followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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

	# Declare many-to-many relationship b/w followers/followed.
	followed = db.relationship('User', # right-side entity (left-side entity is the parent class)
								secondary=followers, # association table used for the relationship
								primaryjoin=(followers.c.follower_id == id), # condition that links the left-side entity (the follower) w/ the assoc table
								secondaryjoin=(followers.c.followed_id == id), # condition that links the right-side entity (the followed) w/ the assoc table
								backref=db.backref('followers', lazy='dynamic'), # how the relationship will be accessed from the right-side entity
								lazy='dynamic') # lazy - execution mode for the query


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

	#### Following methods - add/remove relationships b/w users. ###

	def follow(self, user):
		"""Input: user object, other user object
		   Output: If not already following, make the 
		   given user follow another user by adding an 
		   entry to the association table."""
		if not self.is_following(user):

			# SQLAlchemy handles adding this to the assoc table.
			self.followed.append(user)
			return self

	def unfollow(self, user):
		"""Input: user object, other user object
		   Output: If already following, make the 
		   given user unfollow another user by removing an 
		   entry from the association table."""
		if self.is_following(user):

			# SQLAlchemy handles removing this from the assoc table.
			self.followed.remove(user)
			return self

	def is_following(self, user):
		"""Input: user object, other user object
		   Output: Boolean; True if the given user 
		   is following another user."""

		# Because lazy is 'dynamic', filter returns the query object,
		# not the result of the query. Calling count() executes the 
		# query and returns the count.
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0

	### Misc. queries ###

	def followed_posts(self):
		"""Input: User object
		   Output: Query for posts of followers of the given user"""

		# A query on the Post model/table - returns a query for the posts that 
		# match the given query (not the temp table created by the join/filter).
		return Post.query.join(
			# Join the Post table (left) w/ the followers table (right)
			# given the condition that the followed_id is the user_id of the Post.
			# i.e., if a user isn't followed, they won't show up.
			followers, (followers.c.followed_id == Post.user_id)).filter(
				# Filter the returned (joined) subtable for only those
				# users the given user is following.
			 	followers.c.follower_id == self.id).order_by(
			  		# Order that filtered table by the Post timestamp.
			  		Post.timestamp.desc())

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