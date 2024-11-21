import os
from unittest import TestCase

from flask import session, g
from models import db, User
from helpers import login, logout, confirm_access, get_met_object, get_met_results, Result

os.environ['DATABASE_URL'] = "postgresql:///inspireme_test"

from app import app, CURR_USER_KEY

with app.app_context():
    db.drop_all()
    db.create_all()

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

class UserFunctionsTestCase(TestCase):
    """test helper functions login/logout/confirm_access"""

    def setUp(self):
        """set up test client"""
        with app.app_context():
            User.query.delete()
            db.session.commi()
            
            self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_login(self):
        """login function adds user to session(curr_user_key)"""

        u=User(username='testuser',
            email='email@test.com',
            password='hashed_pw')
        with app.app_context():
            db.session.add(u)
            db.session.commit()
        
        login(u)

        self.assertEqual(session[CURR_USER_KEY], u.id)

    def test_logout(self):
        """logout function removes curr_user_key from session"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
        
        logout()

        self.assertNotIn(CURR_USER_KEY, self.session.data)

    def test_confirm_access_logged_out(self):
        """returns false if no user is logged in"""

        g.user=None
        self.assertFalse(confirm_access(user_id=1))

    def test_confirm_access_other_user(self):
        """returns false if wrong user"""

        g.user=1
        self.assertFalse(confirm_access(user_id=2))
    
    def test_confirm_access_correct_user(self):
        """returns true to indicate user ID matches logged in user"""

        g.user=1
        self.assertTrue(confirm_access(user_id=1))

class ResultsFunctionsTestCase(TestCase):
    """test helper functions for search results"""

    def test_result_object(self):
        """test Result class"""

        name='name', 
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
        self.assertEqual(r1.name, 'name')
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