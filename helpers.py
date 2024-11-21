from flask import session, flash, g
import requests

CURR_USER_KEY = "curr_user"

# user related functions

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

# for MET search result--need to get list of object IDs that match search term, then get full object from the ID
def get_met_results(search_term):
    """get list of object IDs for results from MET search"""

    resp = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q={search_term}")
    res_data=resp.json()
    object_ids=res_data['objectIDs']

    return object_ids

def get_met_object(obj_id):
    """get full object from object_id"""

    resp = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}")
    data=resp.json()

    name=data.get('title')
    artist=data.get('artistDisplayName')
    image=data.get('primaryImage')
    medium=data.get('medium')
    dimensions=data.get('dimensions')
    creation_date=data.get('objectDate')

    result = Result(name, artist, image, medium, dimensions, creation_date)

    return result

class Result():
    """result object from API response. All optional for db object, defaults set to none unless otherwise specified. Will be used to build inspo for DB if saved by user"""

    def __init__(self, name = None, artist = None, image = None, medium = None, dimensions = None, creation_date = None):
        
        self.name = name 
        self.artist = artist
        self.image = image
        self.medium = medium
        self.dimensions = dimensions
        self.creation_date = creation_date

    def __repr__(self):
        r=self
        return f"<name: {r.name}, artist: {r.artist}, image: {r.image}, medium: {r.medium}, dimensions: {r.dimensions}, creation date: {r.creation_date}>"