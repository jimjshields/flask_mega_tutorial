import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Post
from datetime import datetime, timedelta

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

	def test_follow_posts(self):
		
		# Make four users.
		u1 = User(nickname='john', email='john@example.com')
		u2 = User(nickname='susan', email='susan@example.com')
		u3 = User(nickname='mary', email='mary@example.com')
		u4 = User(nickname='david', email='david@example.com')
		db.session.add(u1)
		db.session.add(u2)
		db.session.add(u3)
		db.session.add(u4)

		# Make four posts.
		utcnow = datetime.utcnow()
		p1 = Post(body='post from john', author=u1, timestamp=utcnow + timedelta(seconds=1))
		p2 = Post(body='post from susan', author=u2, timestamp=utcnow + timedelta(seconds=2))
		p3 = Post(body='post from mary', author=u3, timestamp=utcnow + timedelta(seconds=3))
		p4 = Post(body='post from david', author=u4, timestamp=utcnow + timedelta(seconds=4))
		db.session.add(p1)
		db.session.add(p2)
		db.session.add(p3)
		db.session.add(p4)

		# Set up the followers.
		u1.follow(u1)
		u1.follow(u2)
		u1.follow(u4)
		u2.follow(u2)
		u2.follow(u3)
		u3.follow(u3)
		u3.follow(u4)
		u4.follow(u4)
		db.session.add(u1)
		db.session.add(u2)
		db.session.add(u3)
		db.session.add(u4)
		db.session.commit()

		# Check the followed posts of each user.
		f1 = u1.followed_posts().all()
		f2 = u2.followed_posts().all()
		f3 = u3.followed_posts().all()
		f4 = u4.followed_posts().all()
		
		# Check that there are the correct number of posts.
		assert len(f1) == 3
		assert len(f2) == 2
		assert len(f3) == 2
		assert len(f4) == 1

		# Check that the posts are the expected ones and in the right order.
		assert f1 == [p4, p2, p1]
		assert f2 == [p3, p2]
		assert f3 == [p4, p3]
		assert f4 == [p4]



if __name__ == '__main__':
	unittest.main()