"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
# Now we can import app
from app import app
from models import db, User, Message, Follows
from unittest import TestCase


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

        u1 = User.signup(
            "uniqueusername1", "uniqueemail1@email.com", PASSWORD, None)

        u1.id = 1
        db.session.commit()

        m = Message(
            text="Hello World.",
            timestamp=datetime.utcnow(),
            user_id=u.id
        )

    def test_message_model(self):
        """Does basic model work?"""

        self.assertEqual(len(u.messages), 1)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(Message.query.count(), 1)

    def test_text(self):
        """Is the text of the message correct?"""


    def test_timestamp(self):
        """Is the timestamp of the message correct?"""


    def test_user_id(self):
        """Is the user_id of the message correct?"""