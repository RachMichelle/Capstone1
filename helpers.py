from flask import session, flash, g

CURR_USER_KEY = "curr_user"

# user route functions

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

# search results

class Result():
    """build result object from API response"""

    def __init__(self, name, artist, image, medium):
        
        self.name = name 
        self.artist = artist
        self.image = image
        self.medium = medium
