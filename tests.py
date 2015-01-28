import os
import unittest

from config import basedir
from app import app, db
from app.models import User

class TestCase(unittest.TestCase):
	def setUp(self):
		"""Required setup for the tests. 
		   Changes the config variables and creates a test db."""

		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		"""Required teardown for the tests.
		   Removes the session and drops the test db."""
		   
		db.session.remove()
		db.drop_all()

	def test_avatar(self):
		"""Test that the avatar url created for a test user is as expected."""

		u = User(nickname='john', email='john@example.com')
		avatar = u.avatar(128)
		expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
		assert avatar[0:len(expected)] == expected

	def test_make_unique_nickname(self):
		"""Test that the function for creating unique usernames works as expected."""

		u = User(nickname='john', email='john@example.com')
		db.session.add(u)
		db.session.commit()
		nickname = User.make_unique_nickname('john')
		assert nickname != 'john'
		u = User(nickname=nickname, email='susan@example.com')
		db.session.add(u)
		db.session.commit()
		nickname2 = User.make_unique_nickname('john')
		assert nickname2 != 'john'
		assert nickname2 != nickname

	def test_follow(self):
		u1 = User(nickname='john', email='john@example.com')
		u2 = User(nickname='susan', email='susan@example.com')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()

		# Check that a user can't unfollow a user they aren't following.
		assert u1.unfollow(u2) is None

		u = u1.follow(u2)
		db.session.add(u)
		db.session.commit()

		# Check that a user can't follow a user they're following.
		assert u1.follow(u2) is None

		# Check that a user is actually following a user they're following.
		assert u1.is_following(u2)
		assert u1.followed.count() == 1
		assert u1.followed.first().nickname == 'susan'
		assert u2.followers.count() == 1
		assert u2.followers.first().nickname == 'john'

		u = u1.unfollow(u2)

		# Check that a user can unfollow a user they're following.
		assert u is not None
		db.session.add(u)
		db.session.commit()

		# Check that unfollowing works as intended.
		assert not u1.is_following(u2)
		assert u1.followed.count() == 0
		assert u2.followers.count() == 0

if __name__ == '__main__':
	unittest.main()