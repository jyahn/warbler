"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(
            text="Hello World.",
            timestamp="2017-02-28 10:45:16.076174",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(u.messages), 1)
        self.assertEqual(len(u.followers), 0)

    def test_message_model_2(self):
        """Does is_following work as intended?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        m = Message(
            text="Hello World.",
            timestamp="2017-02-28 10:45:16.076174",
            user_id=u1.id
        )

        u1.messages.append(m)
        self.assertEqual(len(u1.messages), 1)
