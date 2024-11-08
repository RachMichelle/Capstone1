"""SQLAlchemy models"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """connect to database"""
    db.app = app
    db.init_app(app)

# *****TO IMPLEMENT LATER*****
# store museums and their endpoints in db and dynamically populate search pages. Allows exploration expansion. 

# class Museum(db.Model):
#     """table of museums available to explore"""

#     __tablename__ = 'museums'

#     id - db.Column(db.Integer, primary_key=True, autoincrement=True)

#     name = db.Column(db.text, nullable=False, unique=True)

#     location = db.Column(db.Text)

#     seach_endpoint = db.Column(db.text, nullable=False)

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
    """saved pieces for users"""

    __tablename__ = "inspos"

    id = db.Column(db.Integer, primary_key=True)
    
    # Save serialized Result object as source. Optional: Users can save stand alone notes for ideas without being attached to search result
    source = db.Column(db.PickleType)

    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', backref='inspos')

    @classmethod
    def make_inspo(cls, source, notes, user_id):
        """create new inspo instance"""

        return cls(source=source, notes=notes, user_id=user_id)