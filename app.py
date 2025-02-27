import os
from dotenv import load_dotenv

from flask import Flask, render_template, redirect, session, flash, g, url_for, request
from random import choice
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Inspo
from forms import LoginForm, RegisterForm, NoteForm, InspoForm
from helpers import login, logout, confirm_access, get_met_results, get_met_object


from sqlalchemy.exc import IntegrityError

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///inspireme'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secret")

# toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

# *********************************************************************************

@app.errorhandler(404)
def page_not_found(e):
    """404 page"""
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
        flash("You're already logged in!", "info")
        return redirect('/')

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate_user(form.username.data.lower(), form.password.data)

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
        # check to see if email already exists
        user = User.email_exists(email=form.email.data.lower())
        if user:
            flash('There is already an account registered with that email', 'warning')
            return render_template('forms/register.html', form=form)
        else:    
            try:
                new_user=User.register_user(
                    username=form.username.data.lower(), 
                    email=form.email.data.lower(),
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
# inspo management
# only accessable to logged-in users

@app.route('/inspo/<int:user_id>', methods = ['GET', 'POST'])
def get_inspo_list(user_id):
    """get list of saved inspo for logged-in user.
    modal forms for add/edit notes--submission to add and edit handled in same route"""

    user = User.query.get_or_404(user_id)
 
    # confirm user is trying to view their own page
    access, (msg, cat)=confirm_access(user.id)
    
    if access == False:
        flash(msg, cat)
        return redirect('/')

    # form for both adding and editing
    form = NoteForm()

    # to edit note--confirm edit with hidden form field containing id for inspo
    # note pre-populated with js
    if request.form.get('inspo_id'):
        
        id = request.form.get('inspo_id')
        inspo = Inspo.query.get_or_404(id)
        updated_note = form.notes.data
        
        if form.validate_on_submit():
            inspo.update_note(updated_note)

            db.session.commit()
             
            flash('Updated!', 'success')
            return redirect(url_for('get_inspo_list', user_id=user.id))

    # to add new stand alone note
    else: 
    
        if form.validate_on_submit():
            notes=form.notes.data

            new_note=Inspo.make_inspo(notes=notes, user_id=g.user.id)

            db.session.add(new_note)
            db.session.commit()

            # clear form field after submission
            form.notes.data=''
        
            flash('Note Added!', 'success')
            return redirect(url_for('get_inspo_list', user_id=user.id))

    return render_template('inspo-list.html', user=user, form=form)

@app.route('/inspo/<int:inspo_id>/delete', methods=['POST'])
def delete_inspo(inspo_id):
    """delete favorite or note"""

    inspo=Inspo.query.get_or_404(inspo_id)

    access, (msg, cat)=confirm_access(inspo.user.id)
   
    if access == False:
        flash(msg, cat)
        return redirect('/')

    db.session.delete(inspo)
    db.session.commit()

    flash('Deleted', 'primary')
    return redirect(url_for('get_inspo_list', user_id=g.user.id))


# *********************************************************************************
# Search Routes 
# Will bed reworked to support multiple museums in future

@app.route('/search/met')
def show_search_met():
    """search form for the Met"""
    museum="The Metropolitan Museum of Art"
    return render_template('search/search.html', museum=museum)

@app.route('/search/results', methods=['GET', 'POST'])
def show_search_results():
    """show search results for given term"""

    search_term  = request.args.get('q')

    # get list of object IDs
    obj_ids = get_met_results(search_term)

    if not obj_ids: 
        return render_template('search/no-results.html', search_term=search_term)

    # get one random result from possible objects
    obj = choice(obj_ids)
    result = get_met_object(obj)

    form=InspoForm()

    # save result as new inspo
    if form.validate_on_submit():

        image=request.form.get('image')
        name=request.form.get('name')
        artist=request.form.get('artist')
        medium=request.form.get('medium')
        dimensions=request.form.get('dimensions')
        creation_date=request.form.get('creation_date')
                         
        notes=form.notes.data

        saved_inspo=Inspo.make_inspo(has_favorite=True, image=image, name=name, artist=artist, medium=medium, dimensions=dimensions, creation_date=creation_date, notes=notes, user_id=g.user.id)

        db.session.add(saved_inspo)
        db.session.commit()

        flash('Saved!', 'success')
        return redirect(url_for('show_search_results', result=result, form=form))


    return render_template('/search/results.html', search_term=search_term, result=result, form=form)