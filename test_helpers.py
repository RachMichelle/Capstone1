import os
from unittest import TestCase

from flask import g
from models import db, User
from helpers import confirm_access, get_met_object, get_met_results, Result

os.environ['DATABASE_URL'] = "postgresql:///inspireme_test"

from app import app

with app.app_context():
    db.drop_all()
    db.create_all()

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

class UserFunctionsTestCase(TestCase):
    """test helper functions"""

    def setUp(self):
        """set up test client"""
        with app.app_context():
            User.query.delete()
            db.session.commit()
            
            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()

    def test_confirm_access_logged_out(self):
        """returns false if no user is logged in"""

        with app.app_context():
            u=User(username='testuser',
                   email='email@test.com',
                   password='hashed_pw')
            db.session.add(u)
            db.session.commit

            g.user=None

            self.assertEqual(confirm_access(user_id=u.id), (False, ('Please log in or register to use that feature!', 'info')))

    def test_confirm_access_other_user(self):
        """returns false if wrong user"""

        with app.app_context():
            u=User(username='testuser',
                   email='email@test.com',
                   password='hashed_pw')
            db.session.add(u)
            db.session.commit

            g.user=u
            
            self.assertEqual(confirm_access(user_id=999), (False, ('You are not authorized to view that page', 'danger')))
    
    def test_confirm_access_correct_user(self):
        """returns true to indicate user ID matches logged in user"""

        with app.app_context():
            u=User(username='testuser',
                   email='email@test.com',
                   password='hashed_pw')
            db.session.add(u)
            db.session.commit

            g.user=u

            self.assertTrue(confirm_access(user_id=g.user.id))

class ResultsFunctionsTestCase(TestCase):
    """test helper functions for search results"""

    def test_result_object(self):
        """test Result class"""

        name='name'
        artist='artist'
        image='image'
        medium='medium'
        dimensions='dimensions'
        creation_date='creation_date'

        r1=Result(name=name, artist=artist, image=image, medium=medium, dimensions=dimensions, creation_date=creation_date)
        # without all parameters defined
        r2=Result(name=name, artist=artist, medium=medium)

        self.assertIsInstance(r1, Result)
        self.assertIsInstance(r2, Result)
        self.assertEqual(r1.name,'name')
        self.assertEqual(r2.artist,'artist')
        # defaults to none if nothing passed in
        self.assertEqual(r2.image, None)

    def test_get_met_results(self):
        """test get list of objects matching search term from MET API, returns a list of object ids"""

        resp = get_met_results('sunflower')

        self.assertIsInstance(resp, list)
        self.assertIn(436524, resp)

    def test_get_met_object(self):
        """test get full object with object id from MET API, turns it into Result object"""

        resp = get_met_object(436524)

        self.assertIsInstance(resp, Result)
        self.assertEqual(resp.name, 'Sunflowers')