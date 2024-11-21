"""SQLAlchemy models"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """connect to database"""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(20), nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        u=self
        return f"<User {u.id}: {u.username}, email: {u.email}>"
    
    @classmethod
    def register_user(cls, username, email, password):
        """make username lowercased, hash pwd & create new User instance"""

        # case-insensitive. All usernames to lowercase to prevent "user" and "User" from being considered different
        lowercased_username=username.lower()

        hash=bcrypt.generate_password_hash(password)
        hashed_pwd=hash.decode('utf8')

        return cls(username=lowercased_username, email=email, password=hashed_pwd)
    
    @classmethod
    def authenticate_user(cls, username, password):
        """check for existing user; if found-confirm correct pwd & return User. If not found or incorrect pwd-return False"""
        
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
class Inspo(db.Model):
    """saved pieces for users, either with associated artwork or as stand-alone note"""

    __tablename__ = "inspos"

    id = db.Column(db.Integer, primary_key=True)

    # indicates stand alone note if False
    has_favorite = db.Column(db.Boolean, nullable=False)
    
    # Optional: Some pieces do not have all info available. Users can save stand alone notes for ideas without being attached to saved favorite. For stand alone notes, content validated on form submit
    notes = db.Column(db.Text, nullable=True)
    
    image = db.Column(db.Text, nullable=True)

    name = db.Column(db.Text, nullable=True)

    artist = db.Column(db.Text, nullable=True)

    medium = db.Column(db.Text, nullable=True)

    dimensions = db.Column(db.Text, nullable=True)

    # not all dates are exact, some give approximations (ex-"19th century") cannot use integer or date format to properly capture data provided
    creation_date = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref='inspos')

    @classmethod
    def make_inspo(cls, notes, user_id, has_favorite=False, image=None, name=None, artist=None, medium=None, dimensions=None, creation_date=None ):
        """create new inspo instance, default None for all art info and has_favorite in case of stand alone note"""

        return cls(notes=notes, user_id=user_id, has_favorite=has_favorite, image=image, name=name, artist=artist, medium=medium, dimensions=dimensions, creation_date=creation_date)