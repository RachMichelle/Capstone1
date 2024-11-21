import os
from unittest import TestCase

from models import db, User, Inspo

os.environ['DATABASE_URL'] = "postgresql:///inspireme_test"

from app import app

with app.app_context():
    db.drop_all()
    db.create_all()

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

class ModelsTestCase(TestCase):
    """tests for user and inspo models"""

    def setUp(self):
        """Create test client"""
        with app.app_context():
            User.query.delete()
            Inspo.query.delete()

            db.session.commit()

            self.client = app.test_client()

    # user model tests

    def test_user_model(self):
        """test user model works"""

        u = User(username='testuser',
            email='email@test.com',
            password='hashed_pw')
        with app.app_context():
            db.session.add(u)
            db.session.commit()

        self.assertIsInstance(u, User)
        self.assertEqual(u.username, 'testuser')
        self.assertEqual(repr(u), f"<User {u.id}: testuser, email: email@test.com>")

    def test_register_user(self):
        """test register classmethod"""

        u = User.register_user(
            username='TestUser2', 
            email='email2@test.com', 
            password="hashed_pw2")

        with app.app_context():
            db.session.add(u)
            db.sessoin.commit()

        self.assertIsInstance(u, User)
        self.assertEqual(u.email, 'email2@test.com')
        # should convert username to lowercased
        self.assertEqual(u.username, 'testuser2')

    def test_authenticate_user(self):
        """test authenticate classmethod"""

        u = User(username='testuser3', 
               email='email3@test.com',
               password='hashed_pw3')
        
        with app.app_context():
            db.session.add(u)
            db.session.commit()

        self.assertFalse(User.authenticate_user('testuser3', 'wrongpw'))
        self.assertEqual(User.authenticate_user('testuser3', 'hashed_pw3'), u)

    # inspo model tests

    def test_inspo_model(self):
        """test inspo model works"""

        # associated user to test relationship
        u = User(username='testuser4', 
               email='email4@test.com',
               password='hashed_pw4')
        with app.app_context():
            db.session.add(u)
            db.session.commit()        

        i=Inspo(has_favorite=True,
                 notes="notes",
                 name='name',
                 artist='artist',
                 image='image',
                 medium='medium',
                 dimensions='dimensions',
                 creation_date='creation_date',
                 user_id=u.id)
        with app.app_context():
            db.session.add(i)
            db.session.commit()

        self.assertIsInstance(1, Inspo)
        self.assertEqual(i.name, 'name')

        # test relationship
        self.assertEqual(i.user.username, u.username)

    def test_make_inspo(self):
        """test make_inspo class method"""

        i = Inspo.make_inspo(has_favorite=True,
                notes="notes",
                name='name',
                artist='artist',
                image='image',
                medium='medium',
                dimensions='dimensions',
                creation_date='creation_date',
                user_id=1)
        # stand-alone note
        i2 = Inspo.make_inspo(notes="notes2",
                user_id=1)
        
        with app.app_context():
            db.session.add_all([i, i2])
            db.session.commit()

        self.assertIsInstance(i, Inspo)
        self.assertIsInstance(i2, Inspo)

        self.assertEqual(i.name, 'name')
        self.assertEqual(i2.notes, 'notes2')

        # defaults to false/None if not specified
        self.assertEqual(i2.name, None)
        self.assertFalse(i2.has_favorite)