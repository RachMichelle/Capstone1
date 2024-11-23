import os
from unittest import TestCase

from models import db, User, Inspo
from flask import g
from helpers import login

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

with app.app_context():
    db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

class UserManagementTestCase(TestCase):
    """tests for user management views (login/register/logout)"""

    def setUp(self):
        """Create test client"""

        with app.app_context():
            User.query.delete()
            Inspo.query.delete()

            self.testuser = User.register_user(username='user',
                                 email='test@email.com',
                                 password='hashed_pw')
            
            db.session.commit()

            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()


    def test_login(self):
        """test login page as signed out user"""

        with self.client as c:
            resp=c.get('/login')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-2">Log In</h1>', html)

    def test_login_already_logged_in(self):
        """test for redirect, login page while already logged in"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            resp=c.get('/login')

            self.assertEqual(resp.status_code, 302)

    def test_login_already_logged_in_redirect(self):
        """test following redirect for login page while already logged in"""
        
        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            resp=c.get('/login', follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Explore</h1>', html)

    def test_register(self):
        """test register page as signed out user"""

        with self.client as c:
            resp=c.get('/register')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(' <h1 class="display-2 mb">Sign Up</h1>', html)

    def test_register_already_logged_in(self):
        """test for redirect, register page while already logged in"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id
            
            resp=c.get('/register')

            self.assertEqual(resp.status_code, 302)

    def test_register_already_logged_in_redirect(self):
        """test following redirect for login page while already logged in"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            resp=c.get('/register', follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Explore</h1>', html)

    def test_logout(self):
        """test log out-redirect"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            resp=c.get('/logout')

            self.assertEqual(resp.status_code, 302)

    def test_logout_redirect(self):
        """test follow redirect for log out"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            resp=c.get('/logout', follow_redirects=True)
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Explore</h1>', html)

class InspoManagementTestCase(TestCase):
    """Test Inspo management routes"""

    def setUp(self):
        """Create test client"""

        with app.app_context():
            User.query.delete()
            Inspo.query.delete()

            self.testuser = User.register_user(username='user',
                                email='test@email.com',
                                password='hashed_pw')
            self.testuser2 = User.register_user(username='user2',
                                email='test2@email.com',
                                password='hashed_pw2')
            
            db.session.commit()

            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()

    def test_get_inspo_list_same_user(self):
        """test get inspo list for user who is logged in"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id
            
            with app.app_context():
                g.user = self.testuser

                resp=c.get(f'/inspo/{self.testuser.id}')
                html=resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('<button class="btn btn-outline-primary float-end" data-bs-toggle="modal" data-bs-target="#add-note-modal">Add A Note</button>', html)

    def test_get_inspo_list_different_user(self):
        """test get inspo list for user not logged in, should redirect"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            with app.app_context():
                g.user = self.testuser
            
                resp=c.get(f'/inspo/{self.testuser2.id}')

                self.assertEqual(resp.status_code, 302)

    def test_get_inspo_list_different_user_redirect(self):
        """test get inspo list for user not logged in, follow redirect"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id
                
            with app.app_context():
                g.user = self.testuser

                resp=c.get(f'/inspo/{self.testuser2.id}', follow_redirects=True)
                html=resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('<h1 class="display-1">Explore</h1>', html)

    def test_delete_inspo(self):
        """test deleting a message"""

        with self.client as c:
            with c.session_transaction() as s:
                    s[CURR_USER_KEY] = self.testuser.id

            with app.app_context():
                g.user = self.testuser

                i=Inspo.make_inspo(user_id=self.testuser.id, notes="note")
                db.session.add(i)
                db.session.commit()

                resp=c.post(f'/inspo/{i.id}/delete')

                inspos=Inspo.query.all()
                inspos_list=[inspo.id for inspo in inspos]

                self.assertEqual(resp.status_code, 302)
                self.assertNotIn(i.id, inspos_list)

class SearchRoutesTestCase(TestCase):
    """Test search routes"""
    
    def setUp(self):
        """Create test client"""

        with app.app_context():
            User.query.delete()
            Inspo.query.delete()

            self.testuser = User.register_user(username='user',
                                 email='test@email.com',
                                 password='hashed_pw')
            
            db.session.commit()

            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()

    def test_show_search_met(self):
        """test show search page for MET api"""

        with self.client as c:
            resp=c.get('/search/met')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-5 my-5 ms-3">The Metropolitan Museum of Art</h1>', html)
    
    def test_search_results_logged_out(self):
        """test search results page for user who is not logged in"""

        with self.client as c:
            with app.app_context():
                g.user=None

                resp=c.get('/search/results', query_string={'q':'sunflower'})
                html=resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('<button class="btn btn-outline-primary" type="submit">Try again</button>', html)
                # will not have button to save result
                self.assertNotIn('<button type="button" class="btn btn-outline-success" data-bs-toggle="modal" data-bs-target="#save-inspo-modal">Save</button>', html)

    def test_search_results_logged_in(self):
        """test search results page for logged in user"""

        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id
            
            resp=c.get('/search/results', query_string={'q':'sunflower'})
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-outline-primary" type="submit">Try again</button>', html)
            # will have button to save result
            self.assertIn('<button type="button" class="btn btn-outline-success" data-bs-toggle="modal" data-bs-target="#save-inspo-modal">Save</button>', html)

    def test_no_results(self):
        """test page when API search returns no results"""

        with self.client as c:
            resp=c.get('/search/results', query_string={'q':'asdfdf'})
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<span class="ms-3">Try a new search</span>', html)

class OtherRoutesTestCase(TestCase):
    """test other miscellaneous routes"""

    def setUp(self):
        """Create test client"""

        with app.app_context():
            User.query.delete()
            Inspo.query.delete()

            self.testuser = User.register_user(username='user',
                                 email='test@email.com',
                                 password='hashed_pw')
            
            db.session.commit()

            self.client = app.test_client()

    def test_home(self):
        """test view homepage(general)"""

        with self.client as c:

            resp=c.get('/')
            html=resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Explore</h1>', html)

    def test_nav_logged_out(self):
        """test nav via homepage for logged out user"""

        with self.client as c:
            with app.app_context():
                g.user=None

                resp=c.get('/')
                html=resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                # login/register options
                self.assertIn('Log In</a></small>', html)
                self.assertIn('Register</a></small>', html)
                # should not have saved inspo link
                self.assertNotIn('My Inspo</a>', html)

    def test_nav_logged_in(self):
        """test nav via homepage for logged in user"""

        with self.client as c:
            with app.app_context():
                g.user = self.testuser

                resp=c.get('/')
                html=resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 200)
                # should have saved inspo link, log out option
                self.assertIn('My Inspo</a>', html)
                self.assertIn('Log Out</a>)</span></small>', html)
                # no login/register options
                self.assertNotIn('Log In</a></small>', html)
                self.assertNotIn('Register</a></small>', html)