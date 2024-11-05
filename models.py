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
        """hash pwd & create new User instance"""

        hash=bcrypt.generate_password_hash(password)
        hashed_pwd=hash.decode('utf8')

        return cls(username=username, email=email, password=hashed_pwd)
    
    @classmethod
    def authenticate_user(cls, username, password):
        """check for existing user; if found-confirm correct pwd & return User. If not found or incorrect pwd-return False"""
        
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False