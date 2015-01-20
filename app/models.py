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

	# tell python how to print the objects of this class
	def __repr__(self):
		return '<User %r>' % (self.nickname)