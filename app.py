import os
from dotenv import load_dotenv

from flask import Flask, render_template, redirect, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Inspo
from forms import LoginForm, RegisterForm
from result import Result

from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

#******fix DB URI to include supabase, set up in .env*********
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///inspireme'))
# ************************************************************
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secret")

toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def login(user):
    """add successfully authenticated user to session"""

    session[CURR_USER_KEY] = user.id

def logout():
    """remove user from session"""

    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)

def confirm_access(user_id):
    """confirm access for page--check for logged in user and check that logged in user id matches user id for page"""

    if not g.user:
        flash('Please log in or register to use that feature!', 'info')
        return False
    if g.user.id != user_id:
        flash('You are not authorized to view that page', 'danger')
        return False

    return True

# *********************************************************************************

@app.errorhandler(404)
def page_not_found(e):
    """custom 404 page"""
    return render_template('404.html'), 404

# *********************************************************************************

@app.route('/')
def show_home():
    """Homepage"""
    return render_template('home.html')

# *********************************************************************************
# # profile management: login/logout/register

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """show login page and handle login form submission"""

    if CURR_USER_KEY in session: 
        flash("You're already logged in!", "info alert-dismissable")
        return redirect('/')

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate_user(form.username.data, form.password.data)

        if user:
            login(user)
            flash("Welcome back!", 'success')
            return redirect('/')

        flash('Invalid credentials--please try again', 'danger')

    return render_template('forms/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """show register page and handle register form submission"""

    if CURR_USER_KEY in session:
        flash("You're already logged in!", "info")
        return redirect('/')
    
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            new_user=User.register_user(
                username=form.username.data, 
                email=form.email.data,
                password=form.password.data,
            )
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('That username is not available--please try another', 'warning') 
            return render_template('forms/register.html', form=form)
        
        login(new_user)
        flash('Account Created!', 'success')
        return redirect('/')

    return render_template('forms/register.html', form=form)

@app.route('/logout')
def logout_user():
    """log out user"""

    logout()
    flash('See you next time!', 'info')
    return redirect('/')

# *********************************************************************************
# inspo management. Full list, single with details
# only accessable to logged-in users

@app.route('/inspo/<int:user_id>')
def get_inspo_list(user_id):
    """get list of saved inspo for logged-in user"""

    user=User.query.get_or_404(user_id)
 
    if not confirm_access(user.id):
        return redirect('/')

    return render_template('inspos/inspo-list.html')

@app.route('/inspo/<int:user_id>/add')
def add_inspo(user_id):
    """add new inspo for logged in user"""

    if not confirm_access(user_id):
        return redirect('/')

    return render_template('/forms/inspo-edit.html')

@app.route('/inspo/<int:inspo_id>/edit')
def edit_inspo(inspo_id):
    """edit existing inspo for logged in user"""
    inspo = Inspo.query.get_or_404(inspo_id)
    # need to set up db relationship for this:
    if not confirm_access(inspo.user.id):
        return redirect('/')

    return render_template('/forms/inspo-edit.html')

# *********************************************************************************
# Search Routes 
# in future, will condense to one route with variable for museum id. For now, setting museum variable to name to pass to single tempalte

@app.route('/search/met')
def show_search_met():
    """search form for the Met"""
    museum="The Metropolitan Museum of Art"
    return render_template('search/search.html', museum=museum)


@app.route('/search/aic')
def show_search_aic():
    """search form for the aic"""
    museum="The Art Institute of Chicago"
    return render_template('search/search.html', museum=museum)

